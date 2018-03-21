from django.contrib import admin
from placeholdr.models import Place, Trip, PlaceReview, TripReview, TripNode
from placeholdr.models import UserProfile


class PlaceAdmin(admin.ModelAdmin):
    list_display = ('userId', 'lat', 'long', 'desc', 'name')


class TripAdmin(admin.ModelAdmin):
    list_display = ('userId', 'desc', 'name')


class PlaceReviewAdmin(admin.ModelAdmin):
    list_display = ('userId', 'placeId', 'stars', 'review')


class TripReviewAdmin(admin.ModelAdmin):
    list_display = ('userId', 'tripId', 'stars', 'review')


class TripNodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'placeId', 'tripId', 'tripPoint')


# Register your models here.
admin.site.register(Place, PlaceAdmin)
admin.site.register(Trip, TripAdmin)
admin.site.register(PlaceReview, PlaceReviewAdmin)
admin.site.register(TripReview, TripReviewAdmin)
admin.site.register(TripNode, TripNodeAdmin)
admin.site.register(UserProfile)
