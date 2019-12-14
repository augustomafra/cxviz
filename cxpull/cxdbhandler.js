var fs = require('fs');
var util = require(phantom.libraryPath + '/util.js');

var csvHeader = [];
var setCsvHeader = function(header) {
    csvHeader = header;
    csvHeader[0] = 'Data';
}

var updateCsv = function(file, line) {
    if (line.length !== csvHeader.length) {
        util.checkError('fail',
            'Error: length mismatch in csv data: ' + line.length + '. Header length: ' + csvHeader.length);
    }
    var lineStr = line.join(';') + '\n';
    if (!fs.exists(file)) {
        header = csvHeader.join(';') + '\n';
        lineStr = header + lineStr;
        fs.write(file, lineStr, 'w');
    } else {
        fs.write(file, lineStr, 'a');
    }
}

var getFileName = function(cxdb, line) {
    return cxdb + '/' + line[0].replace(' (1)', '') + '.csv';
}

var updateDateStamp = function(cxdb, date) {
    var dateStamp = cxdb + '/.datestamp';
    fs.write(dateStamp, date, 'w');
    return date;
}

var getDateStamp = function(cxdb) {
    var dateStamp = cxdb + '/.datestamp';
    if (!fs.exists(dateStamp)) {
        return null;
    }
    return fs.read(dateStamp);
}

var lock = function(cxdb) {
    var lockFile = cxdb + '/.lock';
    if (fs.exists(lockFile)) {
        console.log('Waiting lock on cxdb: ' + cxdb);
    }
    while (fs.exists(lockFile)) {}
    console.log('Locked cxdb directory: ' + cxdb);
    fs.touch(lockFile);
}

var release = function(cxdb) {
    var lockFile = cxdb + '/.lock';
    if (!fs.exists(lockFile)) {
        console.log('Warning: lock on cxdb \'' + cxdb + '\' was not found when releasing database');
    }
    console.log('Unlocked cxdb directory: ' + cxdb);
    fs.remove(lockFile);
}

var removeThousandsSeparator = function(csvLine) {
    csvLine.map(function(item, i, line) {
		line[i] = item.replace('.', '');
	});
}

var updateCxdb = function(cxdb, date, tableData) {
	tableData.forEach(function(line, index) {
        var csvLine = line.slice(1);
        csvLine.unshift(date.toString());
        removeThousandsSeparator(csvLine);
        updateCsv(getFileName(cxdb, line), csvLine);
	});
    return cxdb;
}

module.exports = {
    updateCxdb : updateCxdb,
    updateDateStamp : updateDateStamp,
    getDateStamp : getDateStamp,
    lock : lock,
    release : release,
    setCsvHeader : setCsvHeader
}

