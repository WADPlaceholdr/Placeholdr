function add_place(p_slug){
	
	document.getElementById(p_slug).style.visibility="hidden";
	
	$.ajax({
		type: "POST",
		url: "/placeholdr/ajax/",
		dataType: 'text',
		data: {
			'csrfmiddlewaretoken': getCookie('csrftoken'),
			'task': "get_added_place",
			'slug': p_slug
		},
		success: function (data) {
			
			document.getElementById("added_section").innerHTML = data;
			
		},
		error: function (data) {
			alert("Damn");
			var err = eval("(" + data.responseText + ")");
			alert(err.Message);
		}
	});
	
}

function remove_place(p_slug){
	
	document.getElementById(p_slug + "_added").outerHTML = "";
	document.getElementById(p_slug).style.visibility = "visible";
	
}

function add_bit(p_slug){
	
	$.ajax({
		type: "POST",
		url: "/placeholdr/ajax/",
		dataType: 'text',
		data: {
			'csrfmiddlewaretoken': getCookie('csrftoken'),
			'task': "get_added_place",
			'slug': p_slug
		},
		success: function (data) {
			
			document.getElementById("added_section").innerHTML = data;
			
		},
		error: function (data) {
			alert("Damn");
			var err = eval("(" + data.responseText + ")");
			alert(err.Message);
		}
	});
	
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function remove_place(){
	
	
	
}