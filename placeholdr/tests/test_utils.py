from placeholdr.models import Place, UserProfile, PlaceReview, Trip, TripNode, TripReview
from django.contrib.auth.models import User
from geoposition import Geoposition

# Utilities
def create_user():
    # Create a user
    user = User.objects.get_or_create(username="user", password="pass1357", email="temporary@gmail.com")[0]

    # Link it to a user profile
    user_profile = UserProfile.objects.get_or_create(user=user, bio="I am just a test user", livesIn="Command Line", rep=200)[0]

    return user_profile


def create_place(user):
    i = user.user.id
    place = Place(name="Place " + str(i), position=Geoposition(float(i * 78.2357),float(i * 15.4913)),
                  desc="I'm just a place in location " + str(i), userId=user)
    place.save()

    return place


def create_place_review(user, place):
    review = PlaceReview(userId=user, placeId=place, stars=4, review="Cool cool cool cool")
    review.save()
    return review


def create_trip(user):
    trip = Trip.objects.get_or_create(userId=user, name="Trip " + str(user.user.id), desc="Just a trip")[0]
    return trip


def create_trip_nodes(trip, places):
    trip_nodes = []

    for i in range(0, len(places)):
        node = TripNode(placeId=places[i], tripId=trip, tripPoint=i)
        node.save()
        trip_nodes.append(node)

    return trip_nodes


def create_trip_review(user, trip):
    review = TripReview(userId=user, tripId=trip, stars=3, review="Not enough places")
    review.save()
    return review


def create_multiple_places(user):
    places = []

    # Create place 1 through 4
    for i in range(1, 5):
        place = Place(name="Place " + str(i), position=Geoposition(float(i * 78.2357),float(i * 15.4913)),
                      desc="I'm just a place in location " + str(i), userId=user)
        place.save()
        places.append(place)
    return places


def create_multiple_trips(user):
    trips = []

    # Create trip 1 through 4
    for i in range(1, 5):
        trip = Trip(userId=user, name="Trip " + str(i), desc="I'm just trip number " + str(i))
        trip.save()
        trips.append(trip)
    return trips


def create_top_users():
    users = []
    for i in range(1, 11):
        user = User(username="user" + str(i), password="test")
        user.save()
        up = UserProfile(user=user, rep=i)
        up.save()
        users.append(up)
    return users
