from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User

from django.core.validators import MaxValueValidator

# Create your models here.
class Place(models.Model):
	id = models.IntegerField(unique=True, primary_key=True)
	userId = models.ForeignKey(User)
	lat = models.CharField(max_length=20)
	long = models.CharField(max_length=20)
	desc = models.CharField(max_length=400)
	picLink = models.ImageField(upload_to='place_images', blank=True)
	slug = models.SlugField(unique=True)
	name = models.CharField(max_length=128, unique=True)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Place, self).save(*args, **kwargs)

	def __str__(self):
		return self.name

class Trip(models.Model):
	id = models.IntegerField(unique=True, primary_key=True)
	userId = models.ForeignKey(User)
	desc = models.CharField(max_length=400)
	picLink = models.ImageField(upload_to='trip_images', blank=True)
	name = models.CharField(max_length=128, unique=True)
	slug = models.SlugField(unique=True)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(auto_now=True)

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super(Trip, self).save(*args, **kwargs)

	def __str__(self):
		return self.name
		
class TripNode(models.Model):
	id = models.IntegerField(unique=True, primary_key=True)
	placeId = models.ForeignKey(Place)
	tripId = models.ForeignKey(Trip)
	tripPoint = models.IntegerField()

	def __str__(self):
		return self.tripPoint
		
class PlaceReview(models.Model):
	id = models.IntegerField(unique=True, primary_key=True)
	userId = models.ForeignKey(User)
	placeId = models.ForeignKey(Place)
	# Positive Integer < 5
	stars = models.PositiveIntegerField(validators=[MaxValueValidator(5)])
	review = models.CharField(max_length=400)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.stars
		
class PlaceTag(models.Model):
	id = models.IntegerField(unique=True, primary_key=True)
	userId = models.ForeignKey(User)
	placeId = models.ForeignKey(Place)
	tagText = models.CharField(max_length=400)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(auto_now=True)

	def __str__(self):
		return tagText
		
class TripTag(models.Model):
	id = models.IntegerField(unique=True, primary_key=True)
	userId = models.ForeignKey(User)
	tripId = models.ForeignKey(Trip)
	tagText = models.CharField(max_length=400)
	created_date = models.DateTimeField(auto_now_add=True)
	modified_date = models.DateTimeField(auto_now=True)

	def __str__(self):
		return tagText
		
class TripReview(models.Model):
	id = models.IntegerField(unique=True, primary_key=True)
	userId = models.ForeignKey(User)
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

class UserProfile(models.Model):
	# Links UserProfile to a User model instance
	user = models.OneToOneField(User)

	# Additional attributes
	bio = models.CharField(max_length=400,default="Hello it's me!")
	livesIn = models.CharField(max_length=20, default='Somewhere')
	rep = models.IntegerField(default=0)
	picture = models.ImageField(upload_to='profile_images', blank=True)
	
	# Override this to make it return something useful
	def __str__(self):
		return self.user.username
