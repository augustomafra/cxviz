var page = require('webpage').create();

var cxdbhandler = require(phantom.libraryPath + '/cxdbhandler.js');
var util = require(phantom.libraryPath + '/util.js');

var debug = false;
var setDebug = function(isdebug) {
    debug = isdebug;
}

var errorReportUrl = '';
var setErrorReportUrl = function(url) {
    errorReportUrl = url;
}

page.onConsoleMessage = function(message) {
    if (debug) console.log('  > ' + message);
}

page.onLoadStarted = function() {
    console.log('Loading: ' + url);
}

page.onResourceError = function(error) {
    util.checkError('fail', 'Error: ' + error);
}

var seconds = function(s) { return s * 1000; }
page.settings.resourceTimeout = seconds(180);

var nextDate = function(date, n) {
    var day = new Date(date);
    day.setDate(day.getDate() + n);
    return day;
}

var equalDates = function(date1, date2) {
    return date1.getFullYear() === date2.getFullYear()
        && date1.getMonth() === date2.getMonth()
        && date1.getDate() === date2.getDate();
}

var pageBind = function(pageVar, func, arg) {
    var result = page.evaluate(function(pageVar, func, arg) {
        if (window[pageVar] === undefined) {
            return 'fail';
        }
        return arg ? func(arg) : func();
    }, pageVar, func, arg);
    util.checkError(result, 'Error: \'' + pageVar + '\' was not loaded in the page.');
    return result;
}

var getDate = function() {
    return pageBind('dtBusca', function() { return dtBusca.value; });
}

var getActiveTab = function() {
    return pageBind('tabAtiva', function() { return tabAtiva.value; });
}

var queryDate = function(date) {
    console.log('Reloading page to: ' + date);
    pageBind('dtBusca', function(date) {
        dateArray = [date.getDate(), date.getMonth() + 1, date.getFullYear()];
        dtBusca.value = dateArray.join('/');
        mojarra.jsfcljs(document.getElementById('formPrincipal'),
                        {'btn-consultar' : 'btn-consultar'},
                        '')
    }, date);
}

var selectTab = function(tabName) {
    console.log('Selecting tab: ' + tabName);
    pageBind('setClasseAtiva', function(tabName) { setClasseAtiva(tabName, 1); }, tabName);
}

var getTableHeader = function() {
    return pageBind('tabs', function() {
        var header = tabs
                        .children[1]
                        .children[0]
                        .children[2]
                        .tHead
                        .children[0]
                        .children;
        var headerTitles = [];
        for (var i = 0; i < header.length; ++i) {
            headerTitles.push(header[i].innerText);
        }
        return headerTitles;
    });
}

var getTableData = function() {
    return pageBind('formPrincipal', function() {
        var table = document.getElementsByClassName("grid_zebrada zebra grid_fundos")[0].tBodies[0].children;
        var tableData = [];
        for (var i = 0; i < table.length; ++i) {
            var line = table[i].children;
            var lineData = [];
            for (var j = 0; j < line.length; ++j) {
                lineData.push(line[j].innerText);
            }
            tableData.push(lineData);
        }
        return tableData;
    });
}

var collectData = function(cxdb, date) {
    console.log('Query table for: ' + getDate());
    console.log('Parsing data in tab: ' + getActiveTab());
    console.log('Dumped data to csv database: ' + cxdbhandler.updateCxdb(cxdb, date, getTableData()));
    console.log('Updated "' + cxdb + '" datestamp to ' + cxdbhandler.updateDateStamp(cxdb, date));
}

var releaseAndExit = function(cxdb, status) {
    if (status !== undefined && status !== 0) {
        console.log('If the problem persists, please file a report in ' + errorReportUrl);
    }
    cxdbhandler.release(cxdb);
    if (status === undefined) {
        phantom.exit();
    } else {
        phantom.exit(status);
    }
}

var onPageReady = function(callback) {
    var pollReadyState = function(callback) {
        setTimeout(function(callback) {
            var state = page.evaluate(function() { return document.readyState; });
            if (state === 'complete') {
                callback();
            } else {
                pollReadyState(callback);
            }
        }, 0, callback);
    }
    pollReadyState(callback);
}

var collectDataInRange = function(cxdb, tabName, date, until, onFinished) {
    onPageReady(function() { queryDate(date); });

    page.onLoadFinished = function(status) {
        util.checkError(status, 'Error when reloading page');
        onPageReady(function() { selectTab(tabName); });

        page.onLoadFinished = function(status) {
            util.checkError(status, 'Error when reloading page');
            onPageReady(function() {
                collectData(cxdb, date);
                if (equalDates(date, until)) {
                    if (onFinished !== undefined) {
                        return onFinished();
                    }
                } else {
                    collectDataInRange(cxdb, tabName, nextDate(date, 1), until, onFinished);
                }
            });
        }
    }
}

var pullCxdb = function(url, cxdb) {
    cxdbhandler.lock(cxdb);
    var today = new Date();
    var until = nextDate(today, -5);
    var dateStamp = cxdbhandler.getDateStamp(cxdb);
    var since = nextDate(until, -7);
    if (dateStamp !== null) {
        since = nextDate(new Date(dateStamp), 1);
    }

    if (equalDates(since, nextDate(until, 1))) {
        console.log('Database "' + cxdb + '" is already up to date');
        releaseAndExit(cxdb);
    }

    page.open(url, function(status) {
        try {
            util.checkError(status, 'Error when opening page');
            cxdbhandler.setCsvHeader(getTableHeader());
            collectDataInRange(cxdb, 'RENDA FIXA', since, until, function () {
                collectDataInRange(cxdb, 'AÇÕES', since, until, function () { releaseAndExit(cxdb); });
            });
        } catch(_) {
            releaseAndExit(cxdb, 1);
        }
    });
}

module.exports = {
    pullCxdb : pullCxdb,
    setDebug : setDebug,
    setErrorReportUrl : setErrorReportUrl,
    releaseAndExit : releaseAndExit
}

