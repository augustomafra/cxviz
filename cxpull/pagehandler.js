var page = require('webpage').create();

var cxdbhandler = require(phantom.libraryPath + '/cxdbhandler.js');
var util = require(phantom.libraryPath + '/util.js');

var debug = false;
var setDebug = function(isdebug) {
    debug = isdebug;
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

var selectRendaFixaTab = function() {
    console.log('Selecting tab: RENDA FIXA');
    pageBind('setClasseAtiva', function() { setClasseAtiva('RENDA FIXA', 1); });
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
        var table = formPrincipal
                        .children[6]
                        .children[1]
                        .children[1]
                        .children[0]
                        .children[2]
                        .children[0]
                        .children[2]
                        .children[2]
                        .children;
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
}

var releaseAndExit = function(cxdb, status) {
    cxdbhandler.release(cxdb);
    if (status === undefined) {
        phantom.exit();
    } else {
        phantom.exit(status);
    }
}

var collectDataInRange = function(cxdb, date, until) {
    queryDate(date);

    page.onLoadFinished = function(status) {
        util.checkError(status, 'Error when reloading page');
        selectRendaFixaTab();

        page.onLoadFinished = function(status) {
            util.checkError(status, 'Error when reloading page');
            collectData(cxdb, date);
            if (equalDates(date, until)) {
                cxdbhandler.updateDateStamp(cxdb, date);
                console.log('Updated "' + cxdb + '" datestamp to ' + date);
                releaseAndExit(cxdb);
            } else {
                collectDataInRange(cxdb, nextDate(date, 1), until);
            }
        }
    }
}

var pullCxdb = function(url, cxdb) {
    cxdbhandler.lock(cxdb);
    var today = new Date();
    var yesterday = nextDate(today, -1);
    var dateStamp = cxdbhandler.getDateStamp(cxdb);
    var since = nextDate(today, -7);
    if (dateStamp !== null) {
        since = nextDate(new Date(dateStamp), 1);
    }

    if (since.getDate() === today.getDate()) {
        console.log('Database "' + cxdb + '" is already up to date');
        releaseAndExit(cxdb);
    }

    page.open(url, function(status) {
        try {
            util.checkError(status, 'Error when opening page');
            cxdbhandler.setCsvHeader(getTableHeader());
            collectDataInRange(cxdb, since, yesterday);
        } catch(_) {
            releaseAndExit(cxdb, 1);
        }
    });
}

module.exports = {
    pullCxdb : pullCxdb,
    setDebug : setDebug,
    releaseAndExit : releaseAndExit
}

