from django import template

register = template.Library()

@register.filter(name='times')
def times(number):
    print("NUMBER: "+ number)
    if not number:
        return []
    return range(int(number))

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)