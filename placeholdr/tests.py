from django.db import models
from django.test import TestCase
from placeholdr.models import Place, UserProfile, PlaceReview, Trip, TripNode, TripReview
from placeholdr.forms import UserProfileForm
from django.contrib import auth
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
    user_profile = \
        UserProfile.objects.get_or_create(user=user, bio="I am just a test user", livesIn="Command Line", rep=200)[0]
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


def create_trip(trip, places):
    trip_nodes = []

    for i in range(0, len(places)):
        node = TripNode(placeId=places[i], tripId=trip, tripPoint=i)
        node.save()
        trip_nodes.append(node)

    return trip_nodes


def create_multiple_places(user):
    places = []

    # Create place 1 through 4
    for i in range(1, 5):
        place = Place(name="Place " + str(i), lat=i * 78.2357, long=i * 15.4913,
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

    # Test content of index before populating
    def test_index_empty_content(self):
        # Access with empty database
        response = self.client.get(reverse('index'))

        # Context dictionary is then empty
        self.assertCountEqual(response.context['places'], [])
        self.assertCountEqual(response.context['userProfiles'], [])
        self.assertCountEqual(response.context['trips'], [])

    # With 4 places, make sure they are all displayed in the index (featured = random for now)
    def test_index_displays_four_featured_places(self):
        places = create_multiple_places(create_user())
        response = self.client.get(reverse('index'))

        for i in range(1, 5):
            self.assertIn("Place " + str(i), response.content.decode('ascii'))

    # With 4 trips, make sure they are all displayed in the index (featured = random for now)
    def test_index_displays_four_featured_trips(self):
        trips = create_multiple_trips(create_user())
        response = self.client.get(reverse('index'))

        for i in range(1, 5):
            self.assertIn("Trip " + str(i), response.content.decode('ascii'))

    def test_index_displays_six_top_users(self):
        users = create_top_users()
        response = self.client.get(reverse('index'))

        for i in range(10, 5, -1):
            user = users[i - 1]
            self.assertIn("user" + str(i), response.content.decode('ascii'))


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

    def test_population_script_changes(self):
        # populate
        populate_placeholdr.populate()

        # Check for one user
        u = User.objects.get(username="michael")
        up = UserProfile.objects.get(user=u)
        self.assertEquals(up.rep, 2360)
        self.assertEquals(up.livesIn, 'London')

        # Check for one place
        p = Place.objects.get(name='Papercup Glasgow')
        self.assertEquals(p.lat, "55.876623")
        self.assertEquals(p.long, "-4.285432")

        # Check for one trip
        t = Trip.objects.get(name='Hot and Cold')
        self.assertEquals(t.desc, "Trek in cold cold Iceland before getting warm in a lagoon")


class UrlTests(TestCase):
    # Error messages
    # Test place, trip contains add review when appropriate

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

    # Make sure you can access a user profile
    def test_user_url(self):
        u = create_user()
        response = self.client.get(reverse('show_user', args=[u.user.username]))
        self.assertIn(u.bio, response.content.decode('ascii'))

    # Command line displays "Place matching query does not exist."
    def test_access_place_that_does_not_exist(self):
        response = self.client.get(reverse('show_place', args=['neverland']))

        # Check that it has a response as status code OK is 200
        # self.assertEquals(response.status_code, 200)

        # Check the rendered page is not empty = customised
        self.assertNotEquals(response.content.decode('ascii'), '')

    # Command line displays "Trip matching query does not exist."
    def test_access_trip_that_does_not_exist(self):
        response = self.client.get(reverse('show_trip', args=['perfect-trip']))

        # Check that it has a response as status code OK is 200
        # self.assertEquals(response.status_code, 200)

        # Check the rendered page is not empty = customised
        self.assertNotEquals(response.content.decode('ascii'), '')


class ContentTests(TestCase):
    # TODO
    # Index contains appropriate ratings
    # Check places and trips have maps displayed
    # Check new places
    # Check top places
    # Check new trips
    # Check top trips

    def setUp(self):
        self.user = create_user()
        self.places = create_multiple_places(self.user)
        self.trip = Trip.objects.get_or_create(userId=self.user, name="Trip " + str(self.user.user.id), desc="Just a trip")[0]
        self.trip_nodes = create_trip(self.trip, self.places)

    def test_trip_page_displays_places(self):
        for node in self.trip_nodes:
            response = self.client.get(reverse('show_trip', args=[self.trip.slug]))
            self.assertIn(str(Place.objects.get(name=node.placeId.name)), response.content.decode('ascii'))

    def test_place_page_displays_post_review_when_logged_in(self):
        None

    def test_trip_page_displays_post_review_when_logged_in(self):
        None



class FormTests(TestCase):
    def setUp(self):
        self.user = create_user()

    def test_registration_form_is_displayed_correctly(self):
        None

    def test_registration_form_is_valid(self):
        form_data = {"bio": self.user.bio, "livesIn": self.user.livesIn, "rep": self.user.rep, "picture": None}
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    # TODO
    # Submit place form
    # Submit trip form
    # Review form

    None


class UserTests(TestCase):
    # TODO
    # Test log in
    # Test displayed links when logged in/logged out
    # Test user image shows up top right
    None
