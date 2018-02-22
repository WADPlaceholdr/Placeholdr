from django import template
from placeholdr.models import Category, Place, Trip, UserProfile

register = template.Library()

@register.inclusion_tag('placeholdr/cats.html')
def get_category_list(cat=None):
    return {'cats': Category.objects.all(),
            'act_cat': cat}

def get_place_list():
    return {'places': Category.objects.all()}

def get_user_list():
    return {'users': UserProfile.objects.all().order_by('-rep')}
