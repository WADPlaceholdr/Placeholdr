from django.test import TestCase, Client
from placeholdr.models import Place, UserProfile, PlaceReview, Trip, TripNode, TripReview
from placeholdr.forms import UserForm, PasswordForm, UserProfileForm, SubmitPlaceForm, SubmitTripForm
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import os, population_script
from django.core.urlresolvers import reverse
from placeholdr.tests import test_utils as utils

class ContentTests(TestCase):
    def setUp(self):
        self.user = utils.create_top_users()[0]
        self.places = utils.create_multiple_places(self.user)
        self.trips = utils.create_multiple_trips(self.user)
        self.trip = self.trips[0]

    # Make sure index displays 4 places
    def test_index_displays_four_featured_places(self):
        places = self.places[:4]
        response = self.client.get(reverse('index'))
        hit = 0

        for i in range(1, 6):
            if ("Place " + str(i)) in response.content.decode('ascii'):
                hit += 1

        self.assertEquals(hit, 4)

    # Make sure index displays 4 trips
    def test_index_displays_four_featured_trips(self):
        trips = self.trips[:4]
        response = self.client.get(reverse('index'))
        hit = 0

        for i in range(1, 6):
            if ("Trip " + str(i)) in response.content.decode('ascii'):
                hit += 1

        self.assertEquals(hit, 4)

    def test_index_displays_six_top_users(self):
        response = self.client.get(reverse('index'))

        # users are named user1 through user6
        for i in range(10, 5, -1):
            self.assertIn("user" + str(i), response.content.decode('ascii'))

    def test_new_places_displays_newest_places(self):
        response = self.client.get(reverse('new_places'))

        # places are named Place 1 through Place 5 (newest:5)
        for i in range(5, 0, -1):
            self.assertIn("Place " + str(i), response.content.decode('ascii'))

    def test_new_trips_displays_newest_trips(self):
        response = self.client.get(reverse('new_trips'))

        # trips are named Trip 1 through Trip 5 (newest:5)
        for i in range(5, 0, -1):
            self.assertIn("Trip " + str(i), response.content.decode('ascii'))

    def test_trip_page_displays_places(self):
        trip_nodes = utils.create_trip_nodes(self.trip, self.places)
        for node in trip_nodes:
            response = self.client.get(reverse('show_trip', args=[self.trip.slug]))
            self.assertIn(str(Place.objects.get(name=node.placeId.name)), response.content.decode('utf8'))

    def test_place_page_displays_rating_and_review(self):
        review = utils.create_place_review(self.user, self.places[0])
        response = self.client.get(reverse('show_place', args=['place-1']))
        self.assertIn(str(review.stars), response.content.decode('utf8'))
        self.assertIn(str(review.review), response.content.decode('utf8'))

    def test_trip_page_displays_rating_and_review(self):
        review = utils.create_trip_review(self.user, self.trip)
        response = self.client.get(reverse('show_trip', args=["trip-1"]))
        self.assertIn(str(review.stars), response.content.decode('utf8'))
        self.assertIn(str(review.review), response.content.decode('utf8'))

    def test_user_profile_displays_following(self):
        # get user's profile
        u = utils.create_user()
        response = self.client.get(reverse('show_user', args=[u]))
        self.assertIn("Following: 0", response.content.decode('ascii'))

        # user now follows user1
        u.follows.add(self.user)
        u.save()
        response = self.client.get(reverse('show_user', args=[u]))
        self.assertIn("Following: 1", response.content.decode('ascii'))


class EmptySiteTests(TestCase):
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

    def test_pages_are_displayed_nicely_when_empty(self):
        pages = ['index', 'users',
                 'new_places', 'top_places', 'popular_places',
                 'new_trips', 'top_trips', 'popular_trips']

        for page in pages:
            response = self.client.get(reverse(page))
            if page == 'index':
                self.assertIn("There are no", response.content.decode('ascii'))
                self.assertIn("today", response.content.decode('ascii'))
            else:
                self.assertIn("There are fewer than", response.content.decode('ascii'))
            self.assertTemplateUsed(response, 'placeholdr/base.html')


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
        self.assertEquals(len(trips_in_database), 5)
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

        # Check that it has a response as status code 404 not found (as designed)
        self.assertEquals(response.status_code, 404)

        # Check the rendered page contains appropriate message
        self.assertIn("Place does not exist", response.content.decode('ascii'))

    # Command line will display "Trip matching query does not exist."
    def test_access_trip_that_does_not_exist(self):
        response = self.client.get(reverse('show_trip', args=['perfect-trip']))

        # Check that it has a response as status code 404 not found (as designed)
        self.assertEquals(response.status_code, 404)

        # Check the rendered page contains appropriate
        self.assertIn("Trip does not exist", response.content.decode('ascii'))

    def test_login_redirects_to_index(self):
        # Access login page with appropriate data
        response = self.client.post(reverse('login'), {'username': 'user', 'password': 'pass1357'})

        self.assertRedirects(response, reverse('index'))


class FormTests(TestCase):
    def setUp(self):
        self.user = utils.create_user()
        self.place = utils.create_place(self.user)
        self.trip = utils.create_multiple_trips(self.user)[0]

    def test_registration_form_is_displayed_correctly(self):
        # Access page
        response = self.client.get(reverse('register'))

        # Check right forms are displayed
        self.assertTrue(isinstance(response.context['user_form'], UserForm))
        self.assertTrue(isinstance(response.context['password_form'], PasswordForm))
        self.assertTrue(isinstance(response.context['profile_form'], UserProfileForm))

        user_form = UserForm()
        password_form = PasswordForm()
        profile_form = UserProfileForm()
        self.assertEquals(response.context['user_form'].as_p(), user_form.as_p())
        self.assertEquals(response.context['password_form'].as_p(), password_form.as_p())
        self.assertEquals(response.context['profile_form'].as_p(), profile_form.as_p())

    def test_registration_form_is_valid(self):
        place_pk = Place.objects.all()[0].pk
        trip_pk = Trip.objects.all()[0].pk
        form_data = {"bio": self.user.bio, "livesIn": self.user.livesIn, "picture": None, "favPlace": str(place_pk),
                     "recommendedTrip": str(trip_pk)}
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_provides_error_message(self):
        # Access login page
        response = self.client.post(reverse('login'), {'username': 'wrong', 'password': 'wrongpass'})
        self.assertIn('Invalid login details supplied.', response.content.decode('ascii'))

    def test_submit_place_form_is_displayed_correctly(self):
        # Log in
        self.client.login(username="user", password="pass1357")

        # Access page (login required)
        response = self.client.get(reverse('submit_place'))

        # Check the page is actually accessible and doesn't redirect the user
        self.assertNotEquals(response.status_code, 302)

        # Check the form is the right one
        self.assertTrue(isinstance(response.context['place_form'], SubmitPlaceForm))

        # Check page displays right fields
        self.assertIn("Name".lower(), response.content.decode('ascii').lower())
        self.assertIn("Desc".lower(), response.content.decode('ascii').lower())
        self.assertIn("Position".lower(), response.content.decode('ascii').lower())
        self.assertIn("PicLink".lower(), response.content.decode('ascii').lower())
        # Checks for API
        self.assertIn("maps".lower(), response.content.decode('ascii').lower())

    def test_submit_trip_form_is_displayed_correctly(self):
        # Log in
        self.client.login(username="user", password="pass1357")

        # Access page (login required)
        response = self.client.get(reverse('submit_trip'))

        # Check the page is actually accessible and doesn't redirect the user
        self.assertNotEquals(response.status_code, 302)
        # Check the form is the right one
        self.assertTrue(isinstance(response.context['trip_form'], SubmitTripForm))

        trip_form = SubmitTripForm()
        self.assertEquals(response.context['trip_form'].as_p(), trip_form.as_p())

    def test_submit_trip_with_no_places_should_not_work(self):
        self.client.login(username="user", password="pass1357")
        form_data = {"name": "Let's go on a test trip", "desc": "here we go", "picLink": None, "slug_holder": 0}
        response = self.client.post(reverse('submit_trip'), data=form_data)
        self.assertIn("You need to have at least two places in your trip!", response.content.decode('ascii'))

    def test_registration_and_upload_image_works(self):
        image = SimpleUploadedFile("testuser.jpg", content=open('static/images/logonobg.png', 'rb').read(),
                                   content_type="image/png")
        response = self.client.post(reverse('register'),
                                    {'username': "testuser", "password": "hello", "email": "hello@gmail.com",
                                     "picture": image, "bio": "coolios", "livesIn": "commandLine"})

        # Check user was registered
        self.assertIn('Thank you for registering!'.lower(), response.content.decode('ascii').lower())
        user = User.objects.get(username='testuser')
        user_profile = UserProfile.objects.get(user=user)
        path = os.path.realpath('.') + '/media/profile_images/testuser.jpg'

        # Check file was saved properly
        self.assertTrue(os.path.isfile(path))

        # Delete file
        os.remove(path)


class UserAccessTests(TestCase):
    def setUp(self):
        self.user = utils.create_user()
        self.place = utils.create_place(self.user)

    def test_right_picture_is_displayed(self):
        response = self.client.get(reverse('index'))
        self.assertIn('src="/static/svg/person.svg"'.lower(), response.content.decode('ascii').lower())

        self.client.login(username="user", password="pass1357")
        response = self.client.get(reverse('index'))
        self.assertIn('src="/static/images/defaultuser.png"'.lower(), response.content.decode('ascii').lower())

    def test_log_in(self):
        self.client.login(username="user", password="pass1357")
        u = auth.get_user(self.client)
        self.assertTrue(u.is_authenticated())

    def test_submit_links(self):
        # check links are disabled when user is logged out
        response = self.client.get(reverse('index'))
        self.assertIn(
            '<a class="dropdown-item\n\ndisabled\n\n" href="/placeholdr/submit_place/"'.lower().replace(" ", ""),
            response.content.decode('ascii').lower().replace(" ", ""))
        self.assertIn(
            '<a class="dropdown-item\n\ndisabled\n\n" href="/placeholdr/submit_trip/"'.lower().replace(" ", ""),
            response.content.decode('ascii').lower().replace(" ", ""))

        # now log in user to make sure the links work
        self.client.login(username="user", password="pass1357")
        response = self.client.get(reverse('index'))
        self.assertIn(reverse('submit_place'), response.content.decode('ascii'))
        self.assertIn(reverse('submit_trip'), response.content.decode('ascii'))

    def test_submit_place_redirects_when_not_logged_in(self):
        response = self.client.get(reverse('submit_place'))
        u = auth.get_user(self.client)
        self.assertFalse(u.is_authenticated())
        self.assertEquals(response.status_code, 302)

    def test_submit_trip_redirects_when_not_logged_in(self):
        response = self.client.get(reverse('submit_trip'))
        u = auth.get_user(self.client)
        self.assertFalse(u.is_authenticated())
        self.assertEquals(response.status_code, 302)

    def test_review_box(self):
        response = self.client.get(reverse('show_place', args=["place-test"]))
        self.assertIn("Please login to post a review".lower(), response.content.decode('ascii').lower())

        self.client.login(username="user", password="pass1357")
        response = self.client.get(reverse('show_place', args=["place-test"]))
        self.assertIn("Enter your review here".lower(), response.content.decode('ascii').lower())

    def test_following_features(self):
        # First sure make the follow button is not in the page when unauthenticated
        response = self.client.get(reverse('show_place', args=["place-test"]))
        self.assertNotIn('onclick="user_follow'.lower(), response.content.decode('ascii').lower())

        usertwo = utils.create_top_users()[0]

        # Now access the page as a logged in user
        self.client.login(username="user1", password="test")
        response = self.client.get(reverse('show_place', args=["place-test"]))

        # usertwo doesn't follow user: check button
        self.assertIn("follow_user", response.content.decode('ascii'))

        usertwo.follows.add(self.user)
        usertwo.save()

        # user follows usertwo: check button
        response = self.client.get(reverse('show_place', args=["place-test"]))
        self.assertIn("unfollow_user".lower(), response.content.decode('ascii').lower())

    def test_cannot_change_your_own_rep(self):
        self.client.login(username="user", password="pass1357")
        response = self.client.get(reverse('show_place', args=["place-test"]))
        self.assertNotIn('id="repup"', response.content.decode('ascii'))
        self.assertNotIn('id="repdown"', response.content.decode('ascii'))


