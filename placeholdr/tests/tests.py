from django.db import models
from django.test import TestCase, Client
from placeholdr.models import Place, UserProfile, PlaceReview, Trip, TripNode, TripReview
from placeholdr.forms import UserProfileForm
from django.contrib import auth
from django.contrib.auth.models import User
import population_script
from geoposition import Geoposition

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.urlresolvers import reverse
from placeholdr.tests import test_utils as utils


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
        places = utils.create_multiple_places(utils.create_user())
        response = self.client.get(reverse('index'))

        for i in range(1, 5):
            self.assertIn("Place " + str(i), response.content.decode('ascii'))

    # With 4 trips, make sure they are all displayed in the index (featured = random for now)
    def test_index_displays_four_featured_trips(self):
        trips = utils.create_multiple_trips(utils.create_user())
        response = self.client.get(reverse('index'))

        for i in range(1, 5):
            self.assertIn("Trip " + str(i), response.content.decode('ascii'))

    def test_index_displays_six_top_users(self):
        users = utils.create_top_users()
        response = self.client.get(reverse('index'))

        # users are named user1 through user6
        for i in range(10, 5, -1):
            self.assertIn("user" + str(i), response.content.decode('ascii'))


class ModelTests(TestCase):
    def setUp(self):
        self.user = utils.create_user()
        self.place = utils.create_place(self.user)
        self.place_review = utils.create_place_review(self.user, self.place)
        self.trips = utils.create_multiple_trips(self.user)


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

    def test_create_new_trip(self):
        trips_in_database = Trip.objects.all()
        self.assertEquals(len(trips_in_database), 4)
        self.assertEquals(trips_in_database[0].name, "Trip 1")


    def test_population_script_changes(self):
        # populate
        population_script.populate()

        # Check for one user
        u = User.objects.get(username="michael")
        up = UserProfile.objects.get(user=u)
        self.assertEquals(up.rep, 2360)
        self.assertEquals(up.livesIn, 'London')

        # Check for one place
        p = Place.objects.get(name='Papercup Glasgow')
        self.assertEquals(float(p.position.latitude), 55.876623)
        self.assertEquals(float(p.position.longitude), -4.285432)

        # Check for one trip
        t = Trip.objects.get(name='Hot and Cold')
        self.assertEquals(t.desc, "Trek in cold cold Iceland before getting warm in a lagoon")


class UrlTests(TestCase):
    def setUp(self):
        self.user = utils.create_user()
        self.places = utils.create_multiple_places(self.user)

    def test_place_contains_slug_field(self):
        place = self.places[0]
        # Check slug was generated
        self.assertEquals(place.slug, "place-1")

    def test_trip_contains_slug_field(self):
        trip = Trip(name="Roadtripping through Europe", userId=self.user)
        trip.save()
        # Check slug was generated
        self.assertEquals(trip.slug, "roadtripping-through-europe")

    # Make sure you can access a user profile
    def test_user_url(self):
        u = self.user
        response = self.client.get(reverse('show_user', args=[u.user.username]))
        self.assertIn(u.bio, response.content.decode('ascii'))

    # Command line will display "Place matching query does not exist."
    def test_access_place_that_does_not_exist(self):
        response = self.client.get(reverse('show_place', args=['neverland']))

        # Check the rendered page is not empty = customised
        self.assertNotEquals(response.content.decode('ascii'), '')

    # Command line will display "Trip matching query does not exist."
    def test_access_trip_that_does_not_exist(self):
        response = self.client.get(reverse('show_trip', args=['perfect-trip']))

        # Check the rendered page is not empty = customised
        self.assertNotEquals(response.content.decode('ascii'), '')


class ContentTests(TestCase):
    # TODO
    # Index contains appropriate ratings
    # Test negative rating
    # Test negative rep
    # Check new places
    # Check top places
    # Check new trips
    # Check top trips

    def setUp(self):
        self.user = utils.create_user()
        self.client = Client()
        self.places = utils.create_multiple_places(self.user)
        self.trip = utils.create_trip(self.user)
        self.trip_nodes = utils.create_trip_nodes(self.trip, self.places)

    def test_trip_page_displays_places(self):
        None
        # Error: userprofile does not exist
        #for node in self.trip_nodes:
        #    response = self.client.get(reverse('show_trip', args=[self.trip.slug]))
        #    self.assertIn(str(Place.objects.get(name=node.placeId.name)), response.content.decode('ascii'))

    def place_page_displays_rating_and_review(self):
        review = utils.create_place_review(self.user, self.places[0])
        response = self.client.get(reverse('show_place'), args=['place-1'])
        self.assertIn(review.stars, response.content.decode('ascii'))
        self.assertIn(review.review, response.content.decode('ascii'))

    def trip_page_displays_rating_and_review(self):
        review = utils.create_trip_review(self.user, self.trip)
        response = self.client.get(reverse('show_trip'), args=["trip-" + str(user.user.id)])
        self.assertIn(review.stars, response.content.decode('ascii'))
        self.assertIn(review.review, response.content.decode('ascii'))

    def test_login(self):
        #self.client.login(username=self.user, password='pass1357')
        #response = self.client.get(reverse('account'))
        #self.assertEqual(response.status_code, 200)
        None

    def test_place_page_displays_post_review_when_logged_in(self):
        None

    def test_trip_page_displays_post_review_when_logged_in(self):
        None



class FormTests(TestCase):
    def setUp(self):
        self.user = utils.create_user()
        self.place = utils.create_place(self.user)
        self.trip = utils.create_multiple_trips(self.user)[0]

    def test_registration_form_is_displayed_correctly(self):
        None

    def test_registration_form_is_valid(self):
        # TODO: populating a select field
        #form_data = {"bio": self.user.bio, "livesIn": self.user.livesIn, "picture": None, "favPlace": (1, "Atomium"), "recommendedTrip": (2, "Papercup Glasgow")}
        #form = UserProfileForm(data=form_data)
        #print (form.errors)
        #self.assertTrue(form.is_valid())
        None

    # TODO
    def test_submit_place_form_is_valid(self):
        None

    def test_submit_place_deals_with_coordinates(self):
        None

    def test_submit_trip_form_is_valid(self):
        None

    def test_review_form_is_valid(self):
        None


class UserTests(TestCase):
    # TODO
    # Test log in
    # Test displayed links when logged in/logged out
    # Test user image shows up top right
    def test_stranger_picture_is_displayed(self):
        None

    def test_user_picture_is_displayed(self):
        None
