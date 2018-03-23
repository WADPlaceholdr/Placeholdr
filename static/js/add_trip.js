var slugs_array = [];

function add_place(p_slug){
	
	document.getElementById(p_slug).outerHTML="";
	
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
			
			slugs_array.push(p_slug.replace(/_/gi,"-"));
			document.getElementById("slug_holder").value = slugs_array.join(";") + ";";
			document.getElementById("added_section").innerHTML += data;
			reset_page();
		},
		error: function (data) {
			alert("Damn");
			var err = eval("(" + data.responseText + ")");
			alert(err.Message);
		}
	});
	
}

$(document).ready(function () {

	reset_page();
	slugs_array = [];
	
});

function dedash(one){
	return one.replace(/-/gi,"_");
}

function reset_page(){
	
	var dash_pattern = /(\(.*-.*\))/g;
	var dash_pattern_two = /(id=".*-.*")/g;
	
	document.getElementById("result_section").innerHTML = document.getElementById("result_section").innerHTML.replace(dash_pattern, dedash);
	document.getElementById("added_section").innerHTML = document.getElementById("added_section").innerHTML.replace(dash_pattern, dedash);
	
	document.getElementById("result_section").innerHTML = document.getElementById("result_section").innerHTML.replace(dash_pattern_two, dedash);
	document.getElementById("added_section").innerHTML = document.getElementById("added_section").innerHTML.replace(dash_pattern_two, dedash);
	
}
	
function remove_place(p_slug){
	
	reset_page();
	
	document.getElementById(p_slug + "_added").outerHTML = "";
	
	slugs_array.splice(slugs_array.indexOf(p_slug), 1);
	document.getElementById("slug_holder").value = slugs_array.join(";") + ";";
	
	search_for_places();
	
}

function search_for_places(){

	var dont;

	$.ajax({
		type: "POST",
		url: "/placeholdr/ajax/",
		dataType: 'json',
		data: {
			'csrfmiddlewaretoken': getCookie('csrftoken'),
			'task': "trip_search",
			'q': document.getElementById("searchy").value
		},
		success: function (data) {
			document.getElementById("result_section").innerHTML = "";
			for (var i = 0; i < data.found_places.length; i++){
				dont = false
				for (var j =0; j < slugs_array.length; j++){
					if (data.found_places[i].search(slugs_array[j]) != -1){
						dont = true;
					}
				}
				if (!dont){
					document.getElementById("result_section").innerHTML += data.found_places[i];
				}
			}

			reset_page();
			
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


