import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'placeholdr_project.settings')

import django
django.setup()
from placeholdr.models import Category, Page

def populate():
    # First, we will create lists of dictionaries containing the pages
    # we want to add into each category.
    # Then we will create a dictionary of dictionaries for our categories.
    # This might seem a little bit confusing, but it allows us to iterate
    # through each data structure, and add the data to our models.

    python_pages = [
        {"title": "Official Python Tutorial", "views":5,
         "url":"http://docs.python.org/2/tutorial/"},
        {"title":"How to Think like a Computer Scientist", "views":66,
         "url":"http://www.greenteapress.com/thinkpython/"},
        {"title":"Learn Python in 10 Minutes", "views":98,
         "url":"http://www.korokithakis.net/tutorials/python/"} ]

    django_pages = [
        {"title":"Official Django Tutorial", "views":55,
         "url":"https://docs.djangoproject.com/en/1.9/intro/tutorial01/"},
        {"title":"Django Rocks", "views":12,
         "url":"http://www.djangorocks.com/"},
        {"title":"How to Tango with Django", "views":98,
         "url":"http://www.tangowithdjango.com/"} ]
    
    other_pages = [
            {"title":"Bottle", "views":56,
             "url":"http://bottlepy.org/docs/dev/"},
            {"title":"Flask", "views":5673,
             "url":"http://flask.pocoo.org"} ]
        
    cats = {"Python": {"pages": python_pages, "views":128, "likes":64},
            "Django": {"pages": django_pages, "views": 64, "likes": 32},
            "Other Frameworks": {"pages": other_pages, "views": 32, "likes": 16} }

    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data["views"], cat_data["likes"])
        for p in cat_data["pages"]:
            add_page(c, p["title"], p["url"], p["views"])

    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))

def add_page(cat, title, url, views):
    p = Page.objects.get_or_create(category=cat, title=title)[0]
    p.url = url
    p.views = views
    p.save()
    return p

def add_cat(name,views,likes):
    c = Category.objects.get_or_create(name=name,views=views,likes=likes)[0]
    c.save()
    return c

if __name__ == '__main__':
    print("Starting Placeholdr (tm) population script...")
    populate()
