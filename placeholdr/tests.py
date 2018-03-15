from django.db import models
from django.test import TestCase
from placeholdr.models import Place, UserProfile, PlaceReview, Trip, TripReview
from django.contrib.auth.models import User
import populate_placeholdr


test_user_name="user"
test_user_password="password"
test_user_bio="I am a test user"
test_user_livesIn="earth"
test_user_rep=200

test_place_name="Seed Vault"
test_place_desc="The Svalbard Global Seed Vault is a secure seed bank on the Norwegian island of Spitsbergen"
test_place_id=0
test_place_lat=78.2357
test_place_long=15.4913

test_review_review="Really cold yet leaks as the permafrost is melting"
test_review_id=0
test_review_stars=5

def create_user():
    user = User.objects.create_user(username=test_user_name, password=test_user_password, id=0)
    user_profile = UserProfile.objects.create(user=user, bio=test_user_bio, livesIn=test_user_livesIn, rep=test_user_rep)
    return user_profile


def create_place(user):
    place = Place.objects.create(
        id=test_place_id,
        lat=test_place_lat,
        long=test_place_long,
        desc=test_place_desc,
        name=test_place_name,
        userId=user.user)
    return place

def create_place_review(user, place):
    place_review = PlaceReview.objects.create(
        id=test_review_id,
        review=test_review_review,
        stars=test_review_stars,
        userId=user.user,
        placeId=place)
    return place_review


class ModelTests(TestCase):
    def setUp(self):
        user = create_user()
        user.save()
        place = create_place(user)
        place.save()
        place_review = create_place_review(user, place)
        place_review.save()

    def test_add_user(self):
        # get user object
        user = User.objects.get(username=test_user_name)
        # get userProfile object
        user = UserProfile.objects.get(user=user)

        # Check that User is in database
        users_in_database = UserProfile.objects.all()
        self.assertEquals(len(users_in_database), 1)
        self.assertEquals(users_in_database[0], user)

    def test_add_place(self):
        place = Place.objects.get(name=test_place_name)
        # Check that Place is in database
        places_in_database = Place.objects.all()
        self.assertEquals(len(places_in_database), 1)
        self.assertEquals(places_in_database[0], place)

    def test_add_place_review(self):
        place_review = PlaceReview.objects.get(id=test_review_id)
        # Check that PlaceReview is in database
        place_reviews_in_database = PlaceReview.objects.all()
        self.assertEquals(len(place_reviews_in_database), 1)
        self.assertEquals(place_reviews_in_database[0], place_review)

    def test_population_script_changes(self):
        # populate
        populate_placeholdr.populate()

        # Check for one user
        #u = UserProfile.objects.get(self="michael")
        #self.assertEquals(u.rep, 2360)
        #self.assertEquals(u.livesIn, 'London')

        # Check for one place
        p = Place.objects.get(name='Papercup Glasgpw')
        self.assertEquals(p.lat, "55.876623")
        self.assertEquals(p.long, "-4.285432")

        # Check for one trip
        t = Trip.objects.get(name='Hot and Cold')
        self.assertEquals(t.desc, "Trek in cold cold Iceland before getting warm in a lagoon")


class UrlTests(TestCase):
    def test_place_contains_slug_field(self):
        new_place = Place(name="Mount Everest")
        new_place.save()

        # Check slug was generated
        self.assertEquals(new_place.slug, "mount-everest")

    def test_trip_contains_slug_field(self):
        new_trip = Trip(name="Roadtripping through Europe")
        new_trip.save()

        # Check slug was generated
        self.assertEquals(new_trip.slug, "roadtripping-through-europe")


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