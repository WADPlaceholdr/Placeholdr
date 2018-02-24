import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'placeholdr_project.settings')

import django

django.setup()
from placeholdr.models import User, UserProfile, Place, Trip, TripNode, TripReview, PlaceReview
from django.template.defaultfilters import slugify


def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

    # Much secure
    users = [
        {"username": "one", "password": "pass1357"},
        {"username": "two", "password": "pass1357"},
        {"username": "three", "password": "pass1357"},
        {"username": "four", "password": "pass1357"},
        {"username": "five", "password": "pass1357"},
        {"username": "six", "password": "pass1357"}]

    places = [
        {"userId": 1, "lat": "50.890163106", "long": "4.337998648",
            "desc": "The Atomium was erected in 1958 as part of the World Fair exhibition. "
                    "Modelled on an iron atom that has been magnified 165 billion times, it"
                    " consists of 9 metal spheres. The structure weighs 2400 tons and is 102m high. "
                    "The top sphere has a restaurant and provides panoramic views. The other spheres contain "
                    "exhibition spaces.",
            "name": "Atomium"},
        {"userId": 2, "lat": "55.876623", "long": "-4.285432",
            "desc": "Speciality Coffee & OG Brunch based in Glasgow, Scotland. "
                    "A speciality coffee roaster and cafe, putting avocado on toast since 2012.",
            "name": "Papercup Glasgow"},
        {"userId": 3, "lat": "48.858093", "long": "2.294694",
             "desc": "The French capital's most beloved and most touristic landmark: the Eiffel Tower (la Tour Eiffel)."
                     "The Eiffel Tower was the main exhibit of the Paris Exposition of 1889. "
                     "It was constructed to commemorate the centennial of the French Revolution and "
                     "to demonstrate France's industrial prowess to the world.",
             "name": "The Eiffel Tower"},
        {"userId": 2, "lat": "36.056595", "long": "-112.125092",
            "desc": "The Grand Canyon is one of the seven natural wonders of the world, "
                    "and one of the largest canyons on Earth. It stretches for 450km. "
                    "Parts of the canyon are more than 30km wide and one kilometer deep."
                    "Many writers have tried to describe the wonder of the Grand Canyon, but it "
                    "is beyond words.",
            "name": "Grand Canyon"},
        {"userId": 4, "lat": "55.8721211", "long": "-4.2882005",
            "desc": "Founded in 1451, the University of Glasgow is the fourth oldest university "
                    "in the English-speaking world. The University moved from High Street to Gilmorehill"
                    " in 1870. The campus was originally centred around the buildings erected on the "
                    "top of the hill, designed by George Gilbert Scott.",
            "name": "University of Glasgow"},
        {"userId": 3, "lat": "63.881363", "long": "-22.453115",
            "desc": "Mineral-rich hot water from far beneath the earth forms the spectacular lagoon,"
                    "where a luxurious health spa has been developed in the rugged lava landscape. "
                    "The lagoon's geothermal seawater is known for its positive effects on the skin.",
            "name": "Blue Lagoon"},
        {"userId": 1, "lat": "57.322858", "long": "-4.424382",
            "desc": "Loch Ness is Scotland's most famous loch."
                    "Over 300 million years ago a collision of tectonic plates forced the land to bend and buckle, "
                    "forming high mountains and deep gorges. The depths of these gorges were gradually filled with"
                    " water and a string of lochs were formed; Loch Oich, Loch Lochy and Loch Ness.",
            "name": "Loch Ness"}
    ]

    trips = [
        {"userId": 1, "desc": "Head to Loch Ness from Glasgow before coming back for a coffee in town and see the university's buildings", "name": "A Scottish daytrip"},
        {"userId": 5, "desc": "Ride along some scenic routes and stop at very scenic places", "name": "Nature in the US"},
        {"userId": 5, "desc": "Trek in cold cold Iceland before getting warm in a lagoon", "name": "Hot and Cold"},
        {"userId": 2, "desc": "Have some drinks in Belgium and see some sights", "name": "Beer Trip"},
        {"userId": 3, "desc": "Have a look at some universities and how pretty they are", "name": "Academic roadtrip"},
        {"userId": 2, "desc": "This trip is for coffee fanatics who aren't scared of dying of a coffee overdose by visiting a lot of coffee places", "name": "Hyperactive Coffee"},
    ]

    tripNodes = [
        {"placeId": 1, "tripId": 1, "tripPoint": 0},
        {"placeId": 2, "tripId": 1, "tripPoint": 1},
        {"placeId": 3, "tripId": 2, "tripPoint": 0},
        {"placeId": 4, "tripId": 2, "tripPoint": 1},
        {"placeId": 4, "tripId": 3, "tripPoint": 0},
        {"placeId": 2, "tripId": 3, "tripPoint": 1},
        {"placeId": 5, "tripId": 4, "tripPoint": 0},
        {"placeId": 4, "tripId": 4, "tripPoint": 1},
        {"placeId": 3, "tripId": 4, "tripPoint": 2},
        {"placeId": 1, "tripId": 5, "tripPoint": 0},
        {"placeId": 2, "tripId": 5, "tripPoint": 1}
    ]

    placeReviews = [
        {"userId": 1, "placeId": "6", "stars": 2, "review": "It was nice and warm in the water but way too cold outside. "},
        {"userId": 1, "placeId": "4", "stars": 5, "review": "Very pretty and very warm. Good place for some philosophical thinking. "},
        {"userId": 3, "placeId": "5", "stars": 4, "review": "In spite of the rain, the buildings were very pretty. "},
        {"userId": 4, "placeId": "5", "stars": 3, "review": "Very pretty but I wish you could visit the main building tower as well"},
        {"userId": 2, "placeId": "1", "stars": 3, "review": "Very scenic views as part of my very scenic roadtrip. Very crowded though"},
        {"userId": 4, "placeId": "2", "stars": 5, "review": "Some good coffee to get you ready to write essays. Very nice decorations"},
        {"userId": 6, "placeId": "3", "stars": 1, "review": "I'm afraid of heights"},
    ]

    tripReviews = [
        {"userId": 4, "tripId": 1, "stars": 4, "review": "Some very nice scenery. I didn't see the Loch Ness monster but the good coffee afterwards made up for it"},
        {"userId": 2, "tripId": 2, "stars": 5, "review": "Very dry landscapes but still very pretty"},
        {"userId": 1, "tripId": 3, "stars": 2, "review": "Could be way warmer"},
        {"userId": 6, "tripId": 4, "stars": 5, "review": "A lot of hangovers but definitely worth it"},
        {"userId": 5, "tripId": 5, "stars": 3, "review": "It was nice but it reminded me of the work I'm supposed to be doing"},
        {"userId": 3, "tripId": 6, "stars": 4, "review": "Could be better"},
    ]

    for user in users:
        us = add_user(user["username"], user["password"])

    for place in places:
        p = add_place(place["userId"], place["lat"], place["long"], place["desc"], place["name"])

    for trip in trips:
        t = add_trip(trip["userId"], trip["desc"], trip["name"])

    for tripR in tripReviews:
        tr = add_trip_review(tripR["userId"], tripR["tripId"], tripR["stars"], tripR["review"])

    for placeR in placeReviews:
        pr = add_place_review(placeR["userId"], placeR["placeId"], placeR["stars"], placeR["review"])

    for trip_n in tripNodes:
        t_n = add_trip_node(trip_n["tripId"], trip_n["placeId"], trip_n["tripPoint"])


def add_place(puserId, plat, plong, pdesc, pname):
    p = Place.objects.get_or_create(name=pname, userId=User.objects.get(pk=puserId), lat=plat, long=plong, desc=pdesc,
                                    slug=slugify(pname))[0]
    return p


def add_trip(tuserId, tdesc, tname):
    t = Trip.objects.get_or_create(name=tname, userId=User.objects.get(pk=tuserId), desc=tdesc, slug=slugify(tname))[0]
    return t


def add_trip_node(tnTripId, tnPlaceId, tnTripPoint):
    tn = TripNode.objects.get_or_create(tripId=Trip.objects.get(pk=tnTripId), placeId=Place.objects.get(pk=tnPlaceId),
                                        tripPoint=tnTripPoint)[0]
    return tn


def add_place_review(prUId, prPId, prS, prR):
    pr = PlaceReview.objects.get_or_create(userId=User.objects.get(pk=prUId), placeId=Place.objects.get(pk=prPId),
                                           stars=prS, review=prR)
    return pr


def add_trip_review(trUId, trTId, trS, trR):
    tr = TripReview.objects.get_or_create(userId=User.objects.get(pk=trUId), tripId=Trip.objects.get(pk=trTId),
                                          stars=trS, review=trR)
    return tr


def add_user(name, pword):
    u = User.objects.get_or_create(username=name, password=pword)[0]
    u.save()
    up = UserProfile.objects.get_or_create(user=u)[0]
    up.save()
    return u


if __name__ == '__main__':
    print("Starting Placeholdr (tm) population script...")
    populate()
