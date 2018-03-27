from django import template
from django.utils.encoding import iri_to_uri

register = template.Library()


@register.filter(name='times')
def times(number):
    if not number:
        return []
    return range(int(number))


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='staticmedia')
def staticmedia(link):
    new_link = link.replace('/media/media/', '')
    return new_link

@register.filter
def get_type(value):
    return type(value)