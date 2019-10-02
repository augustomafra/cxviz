module.exports = {
    checkError : function(status, message) {
        if (status === 'fail') {
            console.error(message);
            throw new Error();
        }
    }
}

