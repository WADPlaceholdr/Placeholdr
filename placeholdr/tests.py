from django.db import models
from django.test import TestCase
from placeholdr.models import Place, UserProfile, PlaceReview
from django.contrib.auth.models import User



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