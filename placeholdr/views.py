from django.shortcuts import render
from django.http import HttpResponse
from placeholdr.forms import *
from placeholdr.search import normalize_query, get_query
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from django.db.models import Count
import json, re

# Import User
from django.contrib.auth.models import User

# import 404
from django.http import Http404

# Import Trip
from placeholdr.models import Trip, TripNode, TripReview

# Import Place
from placeholdr.models import Place, PlaceReview

from placeholdr.models import UserProfile

# Import the Tag models
from placeholdr.models import PlaceTag
from placeholdr.models import TripTag

from placeholdr.models import RepRecord

################################################ PLACE ################################################

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
            nbr_reviews = len(place_reviews)
            review_dict = {}
            for star in range(1, 6):
                xStarNbrReview = len(PlaceReview.objects.filter(placeId=place, stars=star))
                if nbr_reviews == 0:
                    review_dict[star] = [xStarNbrReview, 0]
                else:
                    review_dict[star] = [xStarNbrReview, xStarNbrReview / nbr_reviews * 100]

            mapsUrl = "https://www.google.com/maps/embed/v1/place?key=AIzaSyD9HsKLciMeT4H_c-NrIFyEI6vVZgY5GGg&q=" + place.lat + "," + place.long
            review_inf = get_reviews(request, False, place_slug)
            submitter = place.userId
            return render(request,
                          'placeholdr/place.html',
                          {'place': place, 'reviews': place_reviews, 'mapsUrl': mapsUrl, 'review_inf': review_inf,
                           'stars': place.get_stars(), 'review_dict': review_dict, "nbr_reviews": nbr_reviews, "submitter": submitter})
        else:
            return HttpResponse("Invalid place slug supplied.")
    else:
        # Not a POST so display the login form
        return HttpResponseRedirect(reverse('index'))


def top_places(request):
    num_of_places = 6
    if Place.objects.all().count() >= num_of_places:
        top = []
        for place in Place.objects.all():
            star_array = star_helper(place, "place")

            if len(top) < num_of_places:
                top.append(star_array)
            else:
                top = sorted(top, key=lambda x: x[1])
                if star_array[1] > top[0][1]:
                    top[0] = star_array
        top = sorted(top, key=lambda x: x[1], reverse=True)
        return render(request, 'placeholdr/top_places.html', {'top_places': top, 'count': num_of_places})
    else:
        return HttpResponse("Fewer than " + num_of_places + " places exist!")


def new_places(request):
    num_of_places = 5
    new_places = []
    if Place.objects.all().count() >= num_of_places:
        new = Place.objects.order_by('-id')[:num_of_places]
        for place in new:
            new_places.append(star_helper(place, "place"))
        return render(request, 'placeholdr/new_places.html', {'new_places': new_places, 'count': num_of_places})
    else:
        return HttpResponse("Fewer than " + num_of_places + " places exist!")


def popular_places(request):
    num_of_places = 6
    if Place.objects.all().count() >= num_of_places:
        pop = []
        for place in Place.objects.all():
            star_array = star_helper(place, "place")
            if len(pop) < num_of_places:
                pop.append(star_array)
            else:
                pop = sorted(pop, key=lambda x: x[3])
                if star_array[3] > pop[0][3]:
                    pop[0] = star_array
        pop = sorted(pop, key=lambda x: x[3], reverse=True)
        return render(request, 'placeholdr/popular_places.html', {'popular_places': pop, 'count': num_of_places})
    else:
        return HttpResponse("Fewer than " + num_of_places + " places exist!")


@login_required
def submit_place(request):
    # get logged in user object
    user = request.user
    userProfile = UserProfile.objects.get(user_id=user.id)

    # If it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        place_form = SubmitPlaceForm(data=request.POST)
        # If the two forms are valid
        if place_form.is_valid():
            place = place_form.save(commit=False)
            place.userId = userProfile

            # Check if there's a picture
            if 'picLink' in request.FILES:
                place.picLink = request.FILES['picLink']

            # Save the user's form data to the database
            place = place_form.save()
        else:
            print(place_form.errors, place_form.errors)
    else:
        place_form = SubmitPlaceForm()

    return render(request, 'placeholdr/submit_place.html', {'place_form': place_form})


################################################ TRIP ################################################

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
            nbr_reviews = len(trip_reviews)
            review_dict = {}
            for star in range(1, 6):
                xStarNbrReview = len(TripReview.objects.filter(tripId=trip, stars=star))
                if nbr_reviews == 0:
                    review_dict[star] = [xStarNbrReview, 0]
                else:
                    review_dict[star] = [xStarNbrReview, xStarNbrReview / nbr_reviews * 100]
            review_inf = get_reviews(request, True, trip_slug)

            if trip_nodes:
                mapsUrl = "https://www.google.com/maps/embed/v1/directions?key=AIzaSyD9HsKLciMeT4H_c-NrIFyEI6vVZgY5GGg&origin=" + \
                          trip_nodes[0].placeId.lat + "%2C" + trip_nodes[0].placeId.long + "&waypoints="
                for trip_n in trip_nodes:
                    places.append(trip_n.placeId)
                    mapsUrl += trip_n.placeId.lat + "%2C" + trip_n.placeId.long + "|"
                mapsUrl = mapsUrl[:-1]
                mapsUrl += "&destination=" + trip_nodes[len(trip_nodes) - 1].placeId.lat + "%2C" + trip_nodes[
                    len(trip_nodes) - 1].placeId.long
            print(mapsUrl)
            submitter = trip.userId
            return render(request, 'placeholdr/trip.html',
                          {'trip': trip, 'places': places, 'trip_nodes': trip_nodes, 'mapsUrl': mapsUrl,
                           'review_inf': review_inf, 'reviews': trip_reviews, 'stars': trip.get_stars(),
                           "review_dict": review_dict, "nbr_reviews": nbr_reviews, "submitter": submitter})
        else:
            return HttpResponse("Invalid trip slug supplied.")
    else:
        # Not a POST so display the login form
        return HttpResponseRedirect(reverse('index'))


def new_trips(request):
    num_of_places = 5
    new_trips = []
    if Trip.objects.all().count() >= num_of_places:
        new = Trip.objects.order_by('-id')[:num_of_places]
        for trip in new:
            new_trips.append(trip_pic_helper(trip))
        return render(request, 'placeholdr/new_trips.html', {'new_trips': new_trips, 'count': num_of_places})
    else:
        return HttpResponse("Fewer than " + num_of_places + " places exist!")


def top_trips(request):
    num_of_places = 6
    if Trip.objects.all().count() >= num_of_places:
        top = []
        for trip in Trip.objects.all():
            star_array = star_helper(trip, "trip")

            if len(top) < num_of_places:
                top.append(star_array)
            else:
                top = sorted(top, key=lambda x: x[1])
                if star_array[1] > top[0][1]:
                    top[0] = star_array
        top = sorted(top, key=lambda x: x[1], reverse=True)
        top_trips = []
        for trip_plus in top:
            top_trips.append(trip_pic_helper(trip_plus[0]))
        return render(request, 'placeholdr/top_trips.html', {'top_trips': top_trips, 'count': num_of_places})
    else:
        return HttpResponse("Fewer than " + num_of_places + " places exist!")


def popular_trips(request):
    num_of_places = 6
    if Trip.objects.all().count() >= num_of_places:
        pop = []
        for trip in Trip.objects.all():
            star_array = star_helper(trip, "trip")
            if len(pop) < num_of_places:
                pop.append(star_array)
            else:
                pop = sorted(pop, key=lambda x: x[3])
                if star_array[3] > pop[0][3]:
                    pop[0] = star_array
        pop = sorted(pop, key=lambda x: x[3], reverse=True)
        popular_trips = []
        for trip_plus in pop:
            popular_trips.append(trip_pic_helper(trip_plus[0]))
        return render(request, 'placeholdr/popular_trips.html',
                      {'popular_trips': popular_trips, 'count': num_of_places})
    else:
        return HttpResponse("Fewer than " + num_of_places + " places exist!")


@login_required
def submit_trip(request):
	# get logged in user object
	user = request.user
	userProfile = UserProfile.objects.get(user_id=user.id)

	trip_form = SubmitTripForm()
	entry_query = None
	found_places = None
	found = None
	query_string = ''
	search_fields = ('name', 'desc')

	if request.method == "POST":
		trip_form = SubmitTripForm(data=request.POST)
		# If the two forms are valid
		if trip_form.is_valid():
			trip = trip_form.save(commit=False)
			trip.userId = userProfile

			# Check if there's a picture
			if 'picLink' in request.FILES:
				trip.picLink = request.FILES['picLink']

			# Save the user's form data to the database
			trip = trip_form.save()
			pattern = re.compile(r'([^;]+);*')
			counter = 0;
			for p_slug in re.findall(pattern,request.POST.get("slug_holder")):
				place = Place.objects.filter(slug=p_slug)[0]
				TripNode.objects.get_or_create(tripId=trip,placeId=place,tripPoint=counter)
				counter = counter + 1
			
		else:
			print(trip_form.errors, trip_form.errors)

	return render(request, 'placeholdr/submit_trip.html',
				  {'query_string': query_string, 'found': found, 'found_places': found_places, 'trip_form': trip_form})


################################################ PLACE OR TRIP ################################################

def get_reviews(request, isTrip, r_slug):
    if isTrip:
        reviews = TripReview.objects.filter(tripId=Trip.objects.get(slug=r_slug))
        tags = TripTag.objects.filter(tripId=Trip.objects.get(slug=r_slug)).values('tagText').distinct().annotate(
            tagNum=Count('tagText')).order_by('-tagNum')
    else:
        reviews = PlaceReview.objects.filter(placeId=Place.objects.get(slug=r_slug))
        tags = PlaceTag.objects.filter(placeId=Place.objects.get(slug=r_slug)).values('tagText').distinct().annotate(
            tagNum=Count('tagText')).order_by('-tagNum')

    stars = 0
    stars_string = ""
    reviews_array = []
    tags_string = "Currently no tags"

    if tags:
        tags_string = "<ul>"
        for tag in tags:
            tags_string += "<li>#" + tag['tagText'] + " (" + str(tag['tagNum']) + ")" + "</li>"
        tags_string += "</ul>"

    if reviews:
        for review in reviews:
            stars += review.stars
        stars = round(stars / len(reviews))
        for i in range(5):
            if i < stars:
                stars_string += '<img src="/static/images/star.png">'
            else:
                stars_string += '<img src="/static/images/starempty.png">'
    return {'stars_string': stars_string, 'tags_string': tags_string, 'rev_sec': str(
        render(request, 'placeholdr/review_section.html', {'reviews': reviews}).getvalue().decode('utf-8'))}


################################################ USER ################################################

def show_user(request, username):
    # If the request is HTTP POST, try to get the relevant information
    if username:
        # Use request.POST.get('<variable>') instead of .get['<v as
        # it returns None if the value does not exist instead of an error

        # Check if login combination is valid
        user = User.objects.get(username=username)
        userProfile = UserProfile.objects.get(user_id=user.id)

        # If we have a User object, the details are correct
        if userProfile.recommendedTrip:
           recTrip = trip_pic_helper(userProfile.recommendedTrip)
        else:
           recTrip = None
        if userProfile:
            return render(request,
                          'placeholdr/user.html',
                          {'shownUser': user, "shownUserProfile": userProfile, 'recTrip': recTrip})
        else:
            return HttpResponse("Invalid user slug supplied.")
    else:
        # Not a POST so display the login form
        return HttpResponseRedirect(reverse('index'))


def users(request):
    # UserProfile.objects.select_related('user').order_by('-rep')[:nbrOfTops + 2]
    num_of_users = 6
    all_users = UserProfile.objects.all()
    all_users_plus = []
    for user in all_users:
        num_of_reviews = PlaceReview.objects.filter(userId=user.id).count() + TripReview.objects.filter(
            userId=user.id).count()
        all_users_plus.append([user, num_of_reviews])
    if all_users.count() >= num_of_users:
        top_users = []
        active_users = []
        random_users = []
        top_users = UserProfile.objects.select_related('user').order_by('-rep')[:num_of_users]
        random_users = UserProfile.objects.select_related('user').order_by('?')[:num_of_users]
        active_users_plus = sorted(all_users_plus, key=lambda x: x[1], reverse=True)[:num_of_users]
        for user in active_users_plus:
            active_users.append(user[0])
        return render(request, 'placeholdr/users.html',
                      {'top': top_users, 'active': active_users, 'random': random_users, 'count': num_of_users})
    else:
        return HttpResponse("Fewer than " + num_of_users + " places exist!")


################################################ AUTHENTICATION ################################################

def register(request):
    # Boolean for when registration was successful, false initially,
    # then set to true if successful
    registered = False

    # If it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        # Attempt to get information from the form
        user_form = UserForm(data=request.POST)
        password_form = PasswordForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        # If the two forms are valid
        if user_form.is_valid() and password_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()

            # Hash the password then update the user object
            user.set_password(password_form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            # Check if there's a profile picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Sve the UserProfile model instance
            profile.save()
            new_user = authenticate(username=user_form.cleaned_data['username'],
                                    password=password_form.cleaned_data['password'],
                                    )
            login(request, new_user)
            registered = True

        else:

            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        password_form = PasswordForm()
        profile_form = UserProfileForm()

    return render(request, 'placeholdr/register.html',
                  {'user_form': user_form, 'password_form': password_form, 'profile_form': profile_form,
                   'registered': registered})


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
                return render(request, 'placeholdr/login.html', {'error': "Your Placeholdr account is disabled."})
        else:
            # Bad login details provided
            print("Invalid login details: {0}, {1}".format(username, password))
            # return login with error message
            return render(request, 'placeholdr/login.html', {'error': "Invalid login details supplied."})
    else:
        # Not a POST so display the login form
        return render(request, 'placeholdr/login.html', {})


@login_required
def user_logout(request):
    # Since we know they are logged in, we can log them out
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def show_account(request):
    # get logged in user object
    user = request.user
    # get logged in userProfile object
    userProfile = UserProfile.objects.get(user_id=user.id)
    if userProfile.recommendedTrip:
        recTrip = trip_pic_helper(userProfile.recommendedTrip)
    else:
        recTrip = None
    return render(request, 'placeholdr/account.html', {'user': user, "userProfile": userProfile, "recTrip": recTrip})


@login_required
def edit_profile(request):
    # get logged in user object
    user = request.user
    userProfile = UserProfile.objects.get(user_id=user.id)

    # If it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        # Attempt to get information from the form
        user_form = ChangeUserForm(data=request.POST, instance=user)
        profile_form = UserProfileForm(data=request.POST, instance=userProfile)

        # If the two forms are valid
        if user_form.is_valid() and profile_form.is_valid():
            # Save the user's form data to the database
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user

            # Check if there's a profile picture
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Save the UserProfile model instance
            profile.save()
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = ChangeUserForm(instance=user)
        profile_form = UserProfileForm(instance=user)

    return render(request, 'placeholdr/edit_profile.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def change_password(request):
    # get logged in user object
    user = request.user
    userProfile = UserProfile.objects.get(user_id=user.id)

    # If it's a HTTP POST, we're interested in processing form data
    if request.method == 'POST':
        # Attempt to get information from the form
        password_form = ChangePasswordForm(data=request.POST, instance=user)

        # If the two forms are valid
        if password_form.is_valid():
            password = password_form.cleaned_data['password']
            if authenticate(username=user, password=password):
                new_password = password_form.cleaned_data['new_password']
                confirm_new_password = password_form.cleaned_data['confirm_new_password']
                if new_password == confirm_new_password:
                    # Hash the password then update the user object
                    user.set_password(new_password)
                    user.save()
                else:
                    error = "passwords did not match"
                    return render(request, 'placeholdr/change_password.html',
                                  {'password_form': password_form, 'error': error})
            else:
                # Bad login details provided
                print("Invalid login details: {0}, {1}".format(user, password))
                error = "Invalid login details supplied."
                return render(request, 'placeholdr/change_password.html',
                              {'password_form': password_form, 'error': error})

        else:
            print(password_form.errors)
    else:
        password_form = ChangePasswordForm(instance=user)

    return render(request, 'placeholdr/change_password.html', {'password_form': password_form})


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


################################################ OTHER ################################################

def index(request):
    nbrOfTops = 4
    place_list = Place.objects.order_by('?')[:nbrOfTops]
    trip_list = Trip.objects.order_by('?')[:nbrOfTops]
    userProfile_list = UserProfile.objects.select_related('user').order_by('-rep')[:nbrOfTops + 2]
    trip_list_plus_pics = []

    for trip in trip_list:
        trip_list_plus_pics.append(trip_pic_helper(trip))

    context_dict = {'places': place_list, 'userProfiles': userProfile_list, 'trips': trip_list_plus_pics}

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


def handler404(request):
    return render(request, 'placeholdr/404.html', status=404)


def handler500(request):
    return render(request, 'placeholdr/500.html', status=500)


def search(request):
    entry_query = None
    found_places = None
    found_trips = None
    found_users = None
    found = None
    query_string = ''
    search_fields = ('name', 'desc')
    user_search_fields = ('bio', 'user__username')

    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']

        entry_query = get_query(query_string, search_fields)
        found_places = Place.objects.filter(entry_query).order_by('id')
        found_trips = Trip.objects.filter(entry_query).order_by('id')
        found_users = UserProfile.objects.filter(get_query(query_string, user_search_fields)).order_by('user__id')
        found = found_places.exists() or found_trips.exists() or found_users.exists()

    return render(request, 'placeholdr/search.html',
                  {'query_string': query_string, 'found': found, 'found_places': found_places,
                   'found_trips': found_trips, 'found_users': found_users})


################################################ HELPER METHODS ################################################
def trip_pic_helper(trip):
    slice_num = 4
    num_of_nodes = TripNode.objects.filter(tripId=trip.id).count()
    if num_of_nodes < 4:
        slice_num = num_of_nodes
    trip_nodes = TripNode.objects.filter(tripId=trip.id).order_by('?')[:num_of_nodes]
    trip_pics = []
    trip_pics.append(trip)
    for trip_node in trip_nodes:
        trip_pics.append(Place.objects.filter(id=trip_node.placeId.id)[0])
    return trip_pics


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
        place_stars = place_stars / len(place_reviews)
        place_stars_rounded = round(place_stars)
        for i in range(5):
            if i < place_stars_rounded:
                place_stars_string += "\u2605 "
            else:
                place_stars_string += "\u2606 "
    else:
        place_stars_string = "\u2606 \u2606 \u2606 \u2606 \u2606"
    return [place, place_stars, place_stars_string, num_reviews]


def ajax_tasks(request):

	if not request.user.is_authenticated:
		return HttpResponse(status=403)
	if request.method == 'POST':

		is_trip = False
		userProf = UserProfile.objects.get(user=request.user)
		if request.POST.get("task") == "add_place_review":
			review = request.POST.get("review")
			stars = request.POST.get("stars")
			r_slug = request.POST.get("slug")
			if (len(review) == 0 or len(stars) != 1 or len(r_slug) == 0):
				return "error"
			link = Place.objects.get(slug=r_slug)
			PlaceReview.objects.get_or_create(userId=userProf, placeId=link,
											  stars=int(stars), review=review)

		if request.POST.get("task") == "add_trip_review":
			review = request.POST.get("review")
			stars = request.POST.get("stars")
			r_slug = request.POST.get("slug")
			if (len(review) == 0 or len(stars) != 1 or len(r_slug) == 0):
				return "error"
			link = Trip.objects.get(slug=r_slug)
			TripReview.objects.get_or_create(userId=userProf, tripId=link,
											 stars=int(stars), review=review)
			is_trip = True

		if request.POST.get("task") == "add_place_review" or request.POST.get("task") == "add_trip_review":
			tags = re.findall('#(\S*)', review)
			for tag in tags:
				if is_trip:
					TripTag.objects.get_or_create(userId=userProf, tripId=link, tagText=tag)
				else:
					PlaceTag.objects.get_or_create(userId=userProf, placeId=link, tagText=tag)
			return HttpResponse(json.dumps(get_reviews(request, is_trip, r_slug)), content_type='application/json')

		if request.POST.get("task") == "add_place_rep":
			rep_slug = "p_" + str(request.POST.get("slug"))
			tpUser = Place.objects.filter(slug=str(request.POST.get("slug")))[0].userId
		
		if request.POST.get("task") == "add_trip_rep":
			rep_slug = "t_" + str(request.POST.get("slug"))
			tpUser = Trip.objects.filter(slug=str(request.POST.get("slug")))[0].userId
		
		if request.POST.get("task") == "add_place_rep" or request.POST.get("task") == "add_trip_rep":
			value=request.POST.get("rep")
			records = RepRecord.objects.filter(tpSlug=rep_slug,userId=userProf)
			if str(value) == "0":
				if records.count() > 0:
					return HttpResponse(json.dumps({"exists":True, "rep":records[0].rep}), content_type='application/json')
				else:
					return HttpResponse({"exists":False, "rep":0})
			if records.count() > 0:
				UserProfile.objects.filter(id=tpUser.id).update(rep= UserProfile.objects.get(id=tpUser.id).rep - RepRecord.objects.filter(tpSlug=rep_slug, userId=userProf)[0].rep + int(value))
				RepRecord.objects.filter(tpSlug=rep_slug, userId=userProf).update(rep=value)
			else:
				UserProfile.objects.filter(id=tpUser.id).update(rep= UserProfile.objects.get(id=tpUser.id).rep + int(value))
				RepRecord.objects.get_or_create(tpSlug=rep_slug, rep=value, userId=userProf)
			return HttpResponse(json.dumps({"exists":True, "rep":value}), content_type='application/json')
		if request.POST.get("task") == "trip_search":
			trip_form = None
			entry_query = None
			found_places = None
			found = None
			query_string = ''
			search_fields = ('name', 'desc')
			results_list = []
			if request.POST.get("q").strip():
				query_string = request.POST.get('q')
				entry_query = get_query(query_string, search_fields)
				found_places = Place.objects.filter(entry_query).order_by('id')
				found = found_places.exists()
				for found_p in found_places:
					results_list.append(render(request, 'placeholdr/psearch_result.html',{"place":found_p}).getvalue().decode('utf-8'))
			return HttpResponse(json.dumps({'query_string': query_string, 'found': found, 'found_places': results_list}))
		if request.POST.get("task") == "get_added_place":
			return HttpResponse(render(request, 'placeholdr/place_added_bit.html',{"place":Place.objects.get(slug=str(request.POST.get("slug").replace("_","-")))}).getvalue().decode('utf-8'))
			
	else:
		return HttpResponse("Error")