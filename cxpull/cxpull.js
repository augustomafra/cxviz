var argparser = require(phantom.libraryPath + '/argparser.js');
var pagehandler = require(phantom.libraryPath + '/pagehandler.js');

phantom.onError = function(msg, trace) {
    var msgStack = ['cxpull error: ' + msg];
    if (trace && trace.length) {
        msgStack.push('stacktrace:');
        trace.forEach(function(t) {
            msgStack.push(' -> '
                          + (t.file || t.sourceURL)
                          + ': ' + t.line
                          + (t.function ? ' (in function ' + t.function +')' : ''));
        });
    }
    console.log(msgStack.join('\n'));
    pagehandler.releaseAndExit(cxdb, 1);
};

var url = 'http://www.fundos.caixa.gov.br/sipii/pages/public/listar-fundos-internet.jsf';
var errorReportUrl = 'http://fale-conosco.caixa.gov.br/wps/portal/faleconosco/home/formulario/reclamacoes';

var args = {};
try {
    args = argparser.parseSystemArgs();
} catch(_) {
    phantom.exit(1);
}

var cxdb = args.cxdb;
if (args.unlock) {
    try {
        pagehandler.releaseAndExit(cxdb);
    } catch(_) {
        phantom.exit(1);
    }
}

try {
    pagehandler.setDebug(args.debug);
    pagehandler.setErrorReportUrl(errorReportUrl);
    pagehandler.pullCxdb(url, cxdb);
} catch(_) {
    pagehandler.releaseAndExit(cxdb, 1);
}

