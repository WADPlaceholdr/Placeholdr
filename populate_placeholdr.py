import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
				      'placeholdr_project.settings')

import django
django.setup()
from placeholdr.models import User,UserProfile,Place,Trip,TripNode,TripReview,PlaceReview
from django.template.defaultfilters import slugify

def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

	# Much secure
	users = [
		{"username": "one", "password":"pass1357"},
		{"username": "two", "password":"pass1357"},
		{"username": "three", "password":"pass1357"},
		{"username": "four", "password":"pass1357"},
		{"username": "five", "password":"pass1357"},
		{"username": "six", "password":"pass1357"}]
	
	places = [{"userId": 1, "lat":"24","long":"3","desc":"somewhere bad", "name":"Dunoon"},
		{"userId": 2, "lat":"2","long":"43","desc":"somewhere here", "name":"Glasga"},
		{"userId": 3, "lat":"2","long":"34","desc":"somewhere french", "name":"Paree"},
		{"userId": 2, "lat":"2","long":"3","desc":"somewhere deep", "name":"Grand Canyon"},
		{"userId": 4, "lat":"245","long":"3","desc":"somewhere near", "name":"Glasga Uni"},
		{"userId": 3, "lat":"2","long":"35","desc":"somewhere cold", "name":"The Moon"},
		{"userId": 1, "lat":"22","long":"3","desc":"somewhere", "name":"Nowhere"}]

	trips = [
		{"userId":1, "desc":"roadtrip1!", "name":"fun trip alpha"},
		{"userId":5, "desc":"roadtrip2!", "name":"fun trip beta"},
		{"userId":5, "desc":"roadtrip3!", "name":"roadX"},
		{"userId":2, "desc":"roadtrip4!", "name":"loooong"},
		{"userId":3, "desc":"roadtrip5!", "name":"ahh"},
		{"userId":2, "desc":"roadtrip6!", "name":"names r hard"}]
		
	tripNodes = [
		{"placeId":1,"tripId":1,"tripPoint":0},
		{"placeId":2,"tripId":1,"tripPoint":1},
		{"placeId":3,"tripId":2,"tripPoint":0},
		{"placeId":4,"tripId":2,"tripPoint":1},
		{"placeId":4,"tripId":3,"tripPoint":0},
		{"placeId":2,"tripId":3,"tripPoint":1},
		{"placeId":5,"tripId":4,"tripPoint":0},
		{"placeId":4,"tripId":4,"tripPoint":1},
		{"placeId":3,"tripId":4,"tripPoint":2},
		{"placeId":1,"tripId":5,"tripPoint":0},
		{"placeId":2,"tripId":5,"tripPoint":1}]
		
	placeReviews = [{"userId":1, "placeId":2,"stars":5,"review":"Could be better"}]
	
	tripReviews = [{"userId":1, "tripId":2,"stars":5,"review":"Could be better"}]
		
	for user in users:
		us = add_user(user["username"], user["password"])
		
	for place in places:
		p = add_place(place["userId"],place["lat"],place["long"],place["desc"],place["name"])
		
	for trip in trips:
		t = add_trip(trip["userId"],trip["desc"],trip["name"])
		
	for tripR in tripReviews:
		tr = add_trip_review(tripR["userId"],tripR["tripId"],tripR["stars"], tripR["review"])
			
	for placeR in placeReviews:
		pr = add_place_review(placeR["userId"],placeR["placeId"],placeR["stars"], placeR["review"])
		
	for trip_n in tripNodes:
		t_n = add_trip_node(trip_n["tripId"],trip_n["placeId"],trip_n["tripPoint"])

def add_place(puserId, plat, plong, pdesc, pname):
	p = Place.objects.get_or_create(name=pname,userId=User.objects.get(pk=puserId),lat=plat,long=plong,desc=pdesc,slug=slugify(pname))[0]
	return p
	
def add_trip(tuserId, tdesc, tname):
	t = Trip.objects.get_or_create(name=tname,userId=User.objects.get(pk=tuserId),desc=tdesc,slug=slugify(tname))[0]
	return t

def add_trip_node(tnTripId, tnPlaceId, tnTripPoint):
	tn = TripNode.objects.get_or_create(tripId=Trip.objects.get(pk=tnTripId),placeId=Place.objects.get(pk=tnPlaceId),tripPoint=tnTripPoint)[0]
	return tn
	
def add_place_review(prUId, prPId, prS, prR):
	pr = PlaceReview.objects.get_or_create(userId=User.objects.get(pk=prUId), placeId=Place.objects.get(pk=prPId), stars=prS, review=prR)
	return pr
	
def add_trip_review(trUId, trTId, trS, trR):
	tr = TripReview.objects.get_or_create(userId=User.objects.get(pk=trUId), tripId=Trip.objects.get(pk=trTId), stars=trS, review=trR)
	return tr
	
def add_user(name,pword):
	u = User.objects.get_or_create(username=name,password=pword)[0]
	u.save()
	up = UserProfile.objects.get_or_create(user=u)[0]
	up.save()
	return u

if __name__ == '__main__':
    print("Starting Placeholdr (tm) population script...")
    populate()
