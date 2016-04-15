function post(query, index) {
    var form = document.createElement("form");
    form.setAttribute("method", "post");
    form.setAttribute("action", "/tweets");

    var hiddenField = document.createElement("input");
    hiddenField.setAttribute("query", query);
    hiddenField.setAttribute("index", index);
    hiddenField.setAttribute("source", "history-bar-results");

    document.body.appendChild(form);
    form.submit();
}
