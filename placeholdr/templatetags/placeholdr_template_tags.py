from django import template
from placeholdr.models import Place, Trip, UserProfile

register = template.Library()

def get_trip_list():
    return {'trips': Trip.objects.all()}


def get_place_list():
    return {'places': Place.objects.all()}


def get_user_list():
    return {'users': UserProfile.objects.all().order_by('-rep')}
