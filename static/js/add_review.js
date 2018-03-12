/*
function add_place_review(slug){
	fix_stars();
	
	/*
	var xhttp = new XMLHttpRequest();
	var params = "task=add_place_review&slug="+slug+"&review="+document.getElementById("pr_review").value+"&stars="+document.getElementById("pr_stars");
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4 && this.status == 200) {
			document.getElementById("review_section").innerHTML = this.responseText;
		}
	};
	xhttp.open("POST", "/placeholdr/ajax", true);
	xhttp.send(params);
	
}
*/
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

$(document).ready(function() {
	
	$('#rev_submit').click(function(){
		fix_stars();
		$.ajax({
			type: "POST",
			url: "/placeholdr/ajax/",
			dataType: 'json',
			data: {
				'csrfmiddlewaretoken' : getCookie('csrftoken'),
				'task': document.getElementById("task").innerHTML,
				'slug': document.getElementById("slug").innerHTML,
				'review': document.getElementById("r_review").value,
				'stars': document.getElementById("r_stars").value
			},
			success: function(data){
				response = data;
				newInner = "";
				for (var i = 0; i < response.reviews.length; i++){
					newInner += response.reviews[i] + "</br>";
				}
				document.getElementById("review_section").innerHTML = newInner;
				document.getElementById("star_rating").innerHTML = response.stars_string;
				
				document.getElementById("r_review").value = ""
			}
		});
	});
	
});

function fix_stars(){
	if (document.getElementById("r_stars") == null){
		
		return;
		
	}
	
	if (document.getElementById("r_stars").value.length > 1){
		
		document.getElementById('r_stars').value = document.getElementById('r_stars').value.substr(0,1);
		alert("Please enter a number from 1-5");
		
	}
	
	if (document.getElementById('r_stars').value.search("[1-5]") == -1){
		
		document.getElementById('r_stars').value = "";
		alert("Please enter a number from 1-5");
		
	}
}