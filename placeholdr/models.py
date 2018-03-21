from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.utils.encoding import uri_to_iri

from django.core.validators import MaxValueValidator


class UserProfile(models.Model):
    # Links UserProfile to a User model instance
    user = models.OneToOneField(User)

    # Additional attributes
    bio = models.CharField(max_length=400, default="Hello it's me!")
    livesIn = models.CharField(max_length=20, default='The Default Place')
    rep = models.IntegerField(default=0)
    picture = models.ImageField(upload_to='profile_images/', blank=True)
    # need to reference two models that have not yet been created
    # Django doc: "use the name of the model rather than the model object itself"
    favPlace = models.ForeignKey('Place', null=True)
    recommendedTrip = models.ForeignKey('Trip', null=True)

    # Override this to make it return something useful
    def __str__(self):
        return self.user.username


class Place(models.Model):
    userId = models.ForeignKey(UserProfile)
    lat = models.CharField(max_length=20)
    long = models.CharField(max_length=20)
    desc = models.CharField(max_length=400)
    picLink = models.ImageField(upload_to='place_images', blank=True)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=128, unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # returns average stars from reviews
    def get_stars(self):
        # Get PlaceReview Objects related to this place
        reviews = list(PlaceReview.objects.filter(placeId=self.id))
        reviews_sum = 0
        if not reviews:
            return 0.0
        for review in reviews:
            reviews_sum += review.stars
        # return float of average of reviews
        return float(reviews_sum) / len(reviews)

    def get_num_reviews(self):
        num_reviews = len(list(PlaceReview.objects.filter(placeId=self.id)))
        return num_reviews

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Place, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Trip(models.Model):
    userId = models.ForeignKey(UserProfile)
    desc = models.CharField(max_length=400)
    picLink = models.ImageField(upload_to='trip_images', blank=True)
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    # returns average stars from reviews
    def get_stars(self):
        # Get PlaceReview Objects related to this place
        reviews = list(TripReview.objects.filter(tripId=self.id))
        reviews_sum = 0
        if not reviews:
            return 0.0
        for review in reviews:
            reviews_sum += review.stars
        # return float of average of reviews
        return float(reviews_sum) / len(reviews)

    def get_num_reviews(self):
        num_reviews = len(list(TripReview.objects.filter(tripId=self.id)))
        return num_reviews

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Trip, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class TripNode(models.Model):
    placeId = models.ForeignKey(Place)
    tripId = models.ForeignKey(Trip)
    tripPoint = models.IntegerField()

    def __str__(self):
        return self.tripPoint


class PlaceReview(models.Model):
    userId = models.ForeignKey(UserProfile)
    placeId = models.ForeignKey(Place)
    # Positive Integer <= 5
    stars = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    review = models.CharField(max_length=400)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.stars)


class PlaceTag(models.Model):
    userId = models.ForeignKey(UserProfile)
    placeId = models.ForeignKey(Place)
    tagText = models.CharField(max_length=400)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tagText


class TripTag(models.Model):
    userId = models.ForeignKey(UserProfile)
    tripId = models.ForeignKey(Trip)
    tagText = models.CharField(max_length=400)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tagText


class TripReview(models.Model):
    userId = models.ForeignKey(UserProfile)
    tripId = models.ForeignKey(Trip)
    # Positive Integer < 5
    stars = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
    review = models.CharField(max_length=400)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.stars


class Category(models.Model):
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Page(models.Model):
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title
