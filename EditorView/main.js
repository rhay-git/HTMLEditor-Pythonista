function send_to_python(name, param) {
    var iframe = document.createElement("IFRAME");
    iframe.setAttribute("src", name + ":" + param);
    document.documentElement.appendChild(iframe);
    iframe.parentNode.removeChild(iframe);
    iframe = null;
}
console.log = function(log) {
    send_to_python("ios-log", log);
}
console.debug = function(log) {
    send_to_python("ios-debug", log);
}
console.info = function(log) {
    send_to_python("ios-info", log);
}
console.warn = function(log) {
    send_to_python("ios-warn", log);
}
console.error = function(log) {
    send_to_python("ios-error", log);
}
console.alert = function(prompt, msg) {
    send_to_python("ios-alert", prompt + ":" + stringify(msg));
}
window.onerror = (function(error, url, line, col, errorobj) {
   console.error(error + " at " + line + ":" + col);
   console.error(stringify(errorobj));
});
console.log("logging activated");
