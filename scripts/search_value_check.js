function scanTextbox(field, e){
    var key;
    if (window.event) key = window.event.keyCode;
    else if(e) key = e.which;
    var value = strip(field.value);
    if(key == 8 || key == 46){
        if(field.value.length <= 140){
            document.getElementById("alert").style.display = "none";
            document.getElementById("alert").innerHTML = "";
        }
    }
    else{
        if(field.value.length > 140){
            document.getElementById("alert").style.display = "block";
            document.getElementById("alert").innerHTML = "Your search key is too long";
        }
        else if(field.value.length > 0){
            document.getElementById("alert").style.display = "none";
            document.getElementById("alert").innerHTML = "";
        }
    }
}

function process(){
    var value = document.getElementById("searchfield").value;
    value = strip(value);
    if(value.length == 0){
        document.getElementById("alert").style.display = "block";
        document.getElementById("alert").innerHTML = "Your search key is too small";
        return false;
    }
    if(value.length > 140){
        document.getElementById("alert").style.display = "block";
        document.getElementById("alert").innerHTML = "Your search key is too long";
        return false;
    }
    return true;
}

function strip(query){
    //Didn't have time to learn regex. Got it from StackOver.
    return query.replace(/^\s+|\s+$/g,'');
}
