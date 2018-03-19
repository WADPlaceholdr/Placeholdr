from django.db import models
from django.test import TestCase
from placeholdr.models import Place, UserProfile, PlaceReview, Trip, TripNode, TripReview
from django.contrib.auth.models import User
import populate_placeholdr

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
import os


# Utilities
def create_user():
    # Create a user
    user = User.objects.get_or_create(username="user", password="test1357")[0]
    user.set_password(user.password)
    user.save()

    # Link it to a user profile
    user_profile = UserProfile.objects.get_or_create(user=user, bio="I am just a test user", livesIn="Command Line", rep=200)[0]
    user_profile.save()

    return user_profile


def create_place(user):
    i = user.user.id
    place = Place(name="Place " + str(i), lat=i * 78.2357, long=i * 15.4913,
                      desc="I'm just a place in location " + str(i), userId=user)
    place.save()

    return place


def create_place_review(user, place):
    review = PlaceReview(userId=user, placeId=place, stars=4, review="Cool cool cool cool")
    review.save()
    return review


def create_trip(user, places):
    trip = Trip(userId=user, name="Trip " + str(user.user.id), desc="Just a trip")
    trip.save()
    trip_nodes = []
    for i in range(0, len(places)):
        node = TripNode(placeId=places[i].id, tripId=trip.id, userId=user.user.id)
        node.save()
        trip_nodes.append(node)

    return trip_nodes


class IndexTests(TestCase):
    def test_index_contains_featured_places_title(self):
        response = self.client.get(reverse('index'))
        self.assertIn('Featured Places'.lower(), response.content.decode('ascii').lower())

    def test_index_contains_featured_trips_title(self):
        response = self.client.get(reverse('index'))
        self.assertIn('Featured Trips'.lower(), response.content.decode('ascii').lower())

    def test_index_contains_top_users_title(self):
        response = self.client.get(reverse('index'))
        self.assertIn('Top Users'.lower(), response.content.decode('ascii').lower())


class ModelTests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.place = create_place(self.user)
        self.place_review = create_place_review(self.user, self.place)

    def test_create_a_new_user(self):

        # Check that User is in database
        users_in_database = UserProfile.objects.all()
        self.assertEquals(len(users_in_database), 1)
        self.assertEquals(users_in_database[0], self.user)

    def test_create_a_new_place(self):

        # Check that Place is in database
        places_in_database = Place.objects.all()
        self.assertEquals(len(places_in_database), 1)
        self.assertEquals(places_in_database[0], self.place)

    def test_create_new_place_review(self):

        # Check that PlaceReview is in database
        place_reviews_in_database = PlaceReview.objects.all()
        self.assertEquals(len(place_reviews_in_database), 1)
        self.assertEquals(place_reviews_in_database[0], self.place_review)

class PopulateScript(TestCase):

    def test_population_script_changes(self):
        # populate
        populate_placeholdr.populate()

        # Check for one user
        # u = UserProfile.objects.get(self="michael")
        # self.assertEquals(u.rep, 2360)
        # self.assertEquals(u.livesIn, 'London')

        # Check for one place
        p = Place.objects.get(name='Papercup Glasgow')
        self.assertEquals(p.lat, "55.876623")
        self.assertEquals(p.long, "-4.285432")

        # Check for one trip
        t = Trip.objects.get(name='Hot and Cold')
        self.assertEquals(t.desc, "Trek in cold cold Iceland before getting warm in a lagoon")


class UrlTests(TestCase):

    def test_place_contains_slug_field(self):
        place = Place(name="Mount Everest", userId=create_user())
        place.save()
        # Check slug was generated
        self.assertEquals(place.slug, "mount-everest")

    def test_trip_contains_slug_field(self):
        trip = Trip(name="Roadtripping through Europe", userId=create_user())
        trip.save()
        # Check slug was generated
        self.assertEquals(trip.slug, "roadtripping-through-europe")



class ContentTests(TestCase):
    # Index contains appropriate ratings
    # Empty user page (e.g. favourite trip) displays appropriate message
    # Check places and trips have maps displayed
    # Test content of index before/after populating
    # Test index displays no content message

    # Test place that does not exist displays appropriate message
    # Trip that does not exist displays appropriate message
    # User that does not exist displays appropriate message
    None


class FeaturesTests(TestCase):
    # Test visits count works
    # Check search looks through all models
    None


class PlaceTests(TestCase):
    # Check places and trips display tags or no tags yet
    # Test place page displays related trips
    # Test place page displays reviews
    None


class TripTests(TestCase):
    # Check places and trips display tags or no tags yet
    # Test trip page displays reviews
    # Check featured trips are not just random
    None


class FormTests(TestCase):
    # Test upload images works
    # Test forms are displayed correctly
    None


class UserTests(TestCase):
    # Test displayed links when logged in/logged out
    # Test user image shows up top right
    None
