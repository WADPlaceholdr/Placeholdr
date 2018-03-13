from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from placeholdr.forms import UserForm, UserProfileForm
from placeholdr.search import normalize_query, get_query
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from django.utils.encoding import iri_to_uri
import json

# Import User
from django.contrib.auth.models import User

# import 404
from django.http import Http404

# Import Trip
from placeholdr.models import Trip, TripNode, TripReview

# Import Place
from placeholdr.models import Place, PlaceReview

# Import the Category model
from placeholdr.models import Category

# Import the CategoryForm
from placeholdr.forms import CategoryForm

# Import the Page model
from placeholdr.models import Page

from placeholdr.models import UserProfile


# Import the PageForm
from placeholdr.forms import PageForm


def index(request):
	# Query the database for a list of ALL places, trips, users currently stored
	
	
	
	nbrOfTops=4
	place_list = Place.objects.order_by('?')[:nbrOfTops]
	trip_list = Trip.objects.order_by('?')[:nbrOfTops]
	userProfile_list = UserProfile.objects.select_related('user').order_by('-rep')[:nbrOfTops+2]
	place_list_plus = []
	trip_list_plus = []
	
	for place in place_list:
		place_list_plus.append(star_helper(place, "place"))
			
	for trip in trip_list:
			trip_list_plus.append(star_helper(trip, "trip"))
	
	context_dict = {'places' : place_list_plus, 'userProfiles' : userProfile_list, 'trips': trip_list_plus}

	# Render the response and send it back!
	response = render(request, 'placeholdr/index.html', context_dict)

	# Return response back to user, updating any cookies that need changed
	return response

def about(request):	
	return render(request, 'placeholdr/about.html', {})

def team(request):
	return render(request, 'placeholdr/team.html', {})

def contact(request):
	return render(request, 'placeholdr/contact.html', {})

def help(request):
	return render(request, 'placeholdr/help.html', {})
	
def register(request):
	# Boolean for when registration was successful, false initially,
	# then set to true if successful
	registered = False

	# If it's a HTTP POST, we're interested in processing form data
	if request.method == 'POST':
		# Attempt to get information from the form
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)

		# If the two forms are valid
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database
			user = user_form.save()

			# Hash the password then update the user object
			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			# Check if there's a profile picture
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Sve the UserProfile model instance
			profile.save()
			new_user = authenticate(username=user_form.cleaned_data['username'],
									password=user_form.cleaned_data['password'],
									)
			login(request, new_user)
			registered = True

		else:

			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'placeholdr/register.html',  {'user_form': user_form, 'profile_form':profile_form, 'registered': registered})

def user_login(request):
	# If the request is HTTP POST, try to get the relevant information
	if request.method == 'POST':
		# Use request.POST.get('<variable>') instead of .get['<v as
		# it returns None if the value does not exist instead of an error
		username = request.POST.get('username')
		password = request.POST.get('password')

		# Check if login combination is valid
		user = authenticate(username=username, password=password)

		# If we have a User object, the details are correct
		if user:
			# Is the account active?
			if user.is_active:
				if 'remember_me' in request.POST:
					request.session.set_expiry(1209600)  # 2 weeks
				else:
					request.session.set_expiry(0)  # Browser close
				# If valid and active, log in
				login(request, user)
				return HttpResponseRedirect(reverse('index'))
			else:
				# Inactive account
				# return login with error message
				return render(request, 'placeholdr/login.html', {'error':"Your Placeholdr account is disabled."})
		else:
			# Bad login details provided
			print("Invalid login details: {0}, {1}".format(username, password))
			# return login with error message
			return render(request, 'placeholdr/login.html', {'error':"Invalid login details supplied."})
	else:
		# Not a POST so display the login form
		return render(request, 'placeholdr/login.html', {})

@login_required
def restricted(request):
	return render(request, 'placeholdr/restricted.html', {})

@login_required
def user_logout(request):
	# Since we know they are logged in, we can log them out
	logout(request)
	return HttpResponseRedirect(reverse('index'))

# A helper method
def get_server_side_cookie(request, cookie, default_val=None):
	val = request.session.get(cookie)
	if not val:
		val = default_val
	return val

def visitor_cookie_handler(request):
	# If the cookie doesn't exist, the default value of 1 is used
	visits = int(get_server_side_cookie(request, 'visits', '1'))

	last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
	last_visit_time = datetime.strptime(last_visit_cookie[:-7],
										'%Y-%m-%d %H:%M:%S')

	# If it's been more than a day since the last visit...
	if (datetime.now() - last_visit_time).days > 0:
		visits = visits + 1
		# Update the last visit cookie
		request.session['last_visit'] = str(datetime.now())
	else:
		request.session['last_visit'] = last_visit_cookie
		
	# Update/set the visits cookie
	request.session['visits'] = visits

def show_trip(request, trip_slug):
	# If the request is HTTP POST, try to get the relevant information
	if trip_slug:
		# Use request.POST.get('<variable>') instead of .get['<v as
		# it returns None if the value does not exist instead of an error

		# Check if trip object exists
		try:
			trip = Trip.objects.get(slug=trip_slug)
		# if it does not return rendered error page
		except Trip.DoesNotExist as e:
			print(e)
			raise Http404("Trip does not exist")

		
		# If we have a Trip object, the details are correct
		if trip:
			places = []
			mapsUrl = ""
			trip_nodes = TripNode.objects.filter(tripId=trip).order_by("-tripPoint")
			trip_reviews = TripReview.objects.filter(tripId=trip)
			
			review_inf = get_reviews(True, trip_slug)
			
			if trip_nodes:
				mapsUrl="https://www.google.com/maps/embed/v1/directions?key=AIzaSyD9HsKLciMeT4H_c-NrIFyEI6vVZgY5GGg&origin=" + trip_nodes[0].placeId.lat + "%2C" + trip_nodes[0].placeId.long + "&waypoints="
				for trip_n in trip_nodes:
					places.append(trip_n.placeId)
					mapsUrl+= trip_n.placeId.lat + "%2C" + trip_n.placeId.long + "|"
				mapsUrl=mapsUrl[:-1]
				mapsUrl+="&destination=" + trip_nodes[len(trip_nodes)-1].placeId.lat + "%2C" + trip_nodes[len(trip_nodes)-1].placeId.long
			print(mapsUrl)
			return render(request, 'placeholdr/trip.html', {'trip': trip, 'places':places, 'trip_nodes':trip_nodes, 'mapsUrl':mapsUrl,'review_inf':review_inf,'reviews':trip_reviews})
		else:
			return HttpResponse("Invalid trip slug supplied.")
	else:
		# Not a POST so display the login form
		return HttpResponseRedirect(reverse('index'))

def show_place(request, place_slug):
	# If the request is HTTP POST, try to get the relevant information
	if place_slug:
		# Use request.POST.get('<variable>') instead of .get['<v as
		# it returns None if the value does not exist instead of an error
		
		# Check if place object exists
		try:
			place = Place.objects.get(slug=place_slug)
		# if it does not return rendered error page
		except Place.DoesNotExist as e:
			print(e)
			raise Http404("Place does not exist")
                
		# If we have a User object, the details are correct
		if place:
		
			place_reviews = PlaceReview.objects.filter(placeId=place)
			mapsUrl = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyD9HsKLciMeT4H_c-NrIFyEI6vVZgY5GGg&origin=" + place.lat + "%2C" + place.long
			mapsUrl = "https://www.google.com/maps/embed/v1/place?key=AIzaSyD9HsKLciMeT4H_c-NrIFyEI6vVZgY5GGg&q=" + place.lat + "," + place.long
			review_inf = get_reviews(False, place_slug)
		
			return render(request,
		  'placeholdr/place.html',
		  {'place':place, 'reviews':place_reviews, 'mapsUrl':mapsUrl, 'review_inf':review_inf})
		else:
			return HttpResponse("Invalid place slug supplied.")
	else:
		# Not a POST so display the login form
		return HttpResponseRedirect(reverse('index'))
		
def show_user(request, username):
	# If the request is HTTP POST, try to get the relevant information
	if username:
		# Use request.POST.get('<variable>') instead of .get['<v as
		# it returns None if the value does not exist instead of an error

		# Check if login combination is valid
		user = User.objects.get(username=username)
		userProfile = UserProfile.objects.get(user_id=user.id)
                
		# If we have a User object, the details are correct
		if userProfile:
			return render(request,
		  'placeholdr/user.html',
		  {'shownUser':user,"shownUserProfile":userProfile})
		else:
			return HttpResponse("Invalid user slug supplied.")
	else:
		# Not a POST so display the login form
		return HttpResponseRedirect(reverse('index'))

@login_required
def show_account(request):
	# get logged in user object
	user = request.user
	# get logged in userProfile object
	userProfile = UserProfile.objects.get(user_id=user.id)
	return render(request, 'placeholdr/account.html', {'user':user, "userProfile":userProfile})

@login_required
def delete_user(request):
	# get logged in user object
	user = request.user
	# get logged in userProfile object
	userProfile = UserProfile.objects.get(user_id=user.id)
	# Delete both objects
	userProfile.delete()
	user.delete()

	return HttpResponseRedirect(reverse('logout'))

def handler404(request):
	return render(request, 'placeholdr/404.html', status=404)


def handler500(request):
	return render(request, 'placeholdr/500.html', status=500)

def search(request):
	entry_query = None
	found_places = None
	found_trips = None
	found_users = None
	found=None
	query_string = ''
	search_fields=('name', 'desc')
	user_search_fields=('bio', 'user__username')

	if ('q' in request.GET) and request.GET['q'].strip():
		query_string = request.GET['q']

		entry_query = get_query(query_string, search_fields)
		found_places = Place.objects.filter(entry_query).order_by('id')
		found_trips = Trip.objects.filter(entry_query).order_by('id')
		found_users = UserProfile.objects.filter(get_query(query_string, user_search_fields)).order_by('user__id')
		found = found_places.exists() or found_trips.exists() or found_users.exists()

	return render(request,'placeholdr/search.html', {'query_string': query_string, 'found': found, 'found_places': found_places, 'found_trips': found_trips, 'found_users': found_users})
	
def ajax_tasks(request):
	if request.method == 'POST':
	
		if request.POST.get("task") == "add_place_review":
			review = request.POST.get("review")
			stars = request.POST.get("stars")
			r_slug = request.POST.get("slug")
			if (len(review) == 0 or len(stars) != 1 or len(r_slug) == 0):
				return "error"
			PlaceReview.objects.get_or_create(userId=request.user, placeId=Place.objects.get(slug=r_slug),
                                           stars=int(stars), review=review)
			return HttpResponse(json.dumps(get_reviews(False, r_slug)),content_type='application/json')
		if request.POST.get("task") == "add_trip_review":
			review = request.POST.get("review")
			stars = request.POST.get("stars")
			r_slug = request.POST.get("slug")
			if (len(review) == 0 or len(stars) != 1 or len(r_slug) == 0):
				return "error"
			TripReview.objects.get_or_create(userId=request.user, tripId=Trip.objects.get(slug=r_slug),
                                           stars=int(stars), review=review)
			return HttpResponse(json.dumps(get_reviews(True, r_slug)),content_type='application/json')
										   
	else:
		return "Error"

def get_reviews(isTrip, r_slug):
	
	if isTrip:
		reviews = TripReview.objects.filter(tripId=Trip.objects.get(slug=r_slug))
	else:
		reviews = PlaceReview.objects.filter(placeId=Place.objects.get(slug=r_slug))

	stars = 0
	stars_string = ""
	reviews_array = []

	if reviews:
		for review in reviews:
			stars += review.stars
			image = "src='/static/images/eiffel.jpg'"
			userProf = UserProfile.objects.filter(user=review.userId)[0]
			if userProf.picture:
				image = userProf.picture
			to_append = '<div class="card wow animated fadeInUp"><div class="card-body"><h5 class="card-title"><img class="img-thumbnail card-user-picture" ' + image + ' alt="Card image cap">' + review.userId.username + '</h5><p>' + str(review.stars) + '/5</p><p class="card-text">' + review.review + '</p><p class="card-text"><small class="text-muted">Last updated ' + str(review.modified_date) + '</small></p></div></div>'
			reviews_array.append(to_append)
		stars = round(stars/len(reviews))
		for i in range(5):
			if i < stars:
				stars_string += '<img src="/static/images/star.png">'
			else:
				stars_string += '<img src="/static/images/starempty.png">'
	return {'reviews':reviews_array, 'stars_string':stars_string}

def add_place_review(request):

	# If it's a HTTP POST, we're interested in processing form data
	if request.method == 'POST':
		# Attempt to get information from the form
		user_form = UserForm(data=request.POST)
		profile_form = UserProfileForm(data=request.POST)


		# If the two forms are valid
		if user_form.is_valid() and profile_form.is_valid():
			# Save the user's form data to the database
			user = user_form.save()

			# Hash the password then update the user object
			user.set_password(user.password)
			user.save()

			profile = profile_form.save(commit=False)
			profile.user = user

			# Check if there's a profile picture
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']

			# Save the UserProfile model instance
			profile.save()

			registered = True

		else:

			print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request, 'placeholdr/register.html',  {'user_form': user_form, 'profile_form':profile_form, 'registered': registered})
	

def star_helper(place, type):
	num_reviews = PlaceReview.objects.filter(placeId=place.id).count()
	place_stars = 0.0
	place_stars_string = ""
	if type == "place":
		place_reviews = PlaceReview.objects.filter(placeId=place)
	elif type == "trip":
		place_reviews = TripReview.objects.filter(tripId=place)

	if place_reviews:
		for place_r in place_reviews:
			place_stars += place_r.stars
		place_stars = place_stars/len(place_reviews)
		place_stars_rounded = round(place_stars)
		for i in range(5):
			if i < place_stars_rounded:
				place_stars_string += "\u2605 "
			else:
				place_stars_string += "\u2606 "
	else:
		place_stars_string = "\u2606 \u2606 \u2606 \u2606 \u2606"
	return [place, place_stars, place_stars_string, num_reviews]
	
def top_places(request):
                
	# If we have a User object, the details are correct
	num_of_places = 5
	if Place.objects.all().count() >= num_of_places:
		top = []
		for place in Place.objects.all():
			star_array = star_helper(place, "place")
			
			if len(top) < num_of_places:
				top.append(star_array)
			else:
				top = sorted(top,key=lambda x: x[1])
				if star_array[1] > top[0][1]:
					top[0] = star_array
		top = sorted(top,key=lambda x: x[1], reverse=True)
		return render(request, 'placeholdr/top_places.html',{'top_places': top, 'count': num_of_places})
	else:
		return HttpResponse("Fewer than " + num_of_places + " places exist!")
		
def new_places(request):
                
	# If we have a User object, the details are correct
	num_of_places = 5
	new_places = []
	if Place.objects.all().count() >= num_of_places:
		new = Place.objects.order_by('-id')[:num_of_places]
		for place in new:
			new_places.append(star_helper(place, "place"))
		return render(request, 'placeholdr/new_places.html',{'new_places': new_places, 'count': num_of_places})
	else:
		return HttpResponse("Fewer than " + num_of_places + " places exist!")
		
def popular_places(request):
                
	# If we have a User object, the details are correct
	num_of_places = 5
	if Place.objects.all().count() >= num_of_places:
		pop = []
		for place in Place.objects.all():
			star_array = star_helper(place, "place")
			if len(pop) < num_of_places:
				pop.append(star_array)
			else:
				pop = sorted(pop,key=lambda x: x[3])
				if star_array[3] > pop[0][3]:
					pop[0] = star_array
		pop = sorted(pop,key=lambda x: x[3], reverse=True)
		return render(request, 'placeholdr/popular_places.html',{'popular_places': pop, 'count': num_of_places})
	else:
		return HttpResponse("Fewer than " + num_of_places + " places exist!")