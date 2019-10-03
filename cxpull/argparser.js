var fs = require('fs');
var system = require('system');

var util = require(phantom.libraryPath + '/util.js');

module.exports = {
    parseSystemArgs : function() {
        var args = system.args;
        if (args.length !== 3 && args.length !== 4) {
            util.checkError('fail', 'Error: Incorrect number of arguments.\nUsage: cxpull --cxdb path/to/cxdb');
        }
        var cxdbSwitch = args.indexOf('--cxdb');
        if (cxdbSwitch === -1) {
            util.checkError('fail', 'Error: Missing switch \'--cxdb\'.\nUsage: cxpull --cxdb path/to/cxdb');
        }
        var cxdbArg = cxdbSwitch + 1;
        if (cxdbArg >= args.length) {
            util.checkError('fail', 'Error: Missing cxdb path.\nUsage: cxpull --cxdb path/to/cxdb');
        }
        var cxdb = args[cxdbArg];
        if (!fs.isDirectory(cxdb)) {
            util.checkError('fail', 'Error: Unable to find cxdb path: ' + cxdb);
        }
        var debug = args.indexOf('--debug') !== -1;
        return {cxdb : cxdb, debug : debug};
    }
}

