from django.conf.urls import url
from placeholdr import views

urlpatterns = [
    # Index page
    url(r'^$', views.index, name='index'),
    # About page
    url(r'^about/', views.about, name='about'),
    # search results page
    url(r'^search/$', views.search, name='search'),
    # Ajax page
    url(r'^ajax/$', views.ajax_tasks, name='ajax_tasks'),

    # User page
    url(r'^user/(?P<username>\w+)/$', views.show_user, name='show_user'),
    # Team page
    url(r'^team/', views.team, name='team'),
    # Contact page
    url(r'^contact-us/', views.contact, name='contact'),
    # Help page
    url(r'^help/', views.help, name='help'),

    ## Account related URLS
    # Register page
    url(r'^register/$', views.register, name='register'),
    # Login page
    url(r'^login/$', views.user_login, name='login'),
    # Restricted page
    url(r'^restricted/', views.restricted, name='restricted'),
    # Account page
    url(r'^account/$', views.show_account, name='account'),
    # Edit account page
    url(r'^account/edit', views.edit_profile, name='edit_profile'),
    # Change password page
    url(r'^account/password', views.change_password, name='change_password'),
    # logout page
    url(r'^logout/$', views.user_logout, name='logout'),
    # Delete account page
    url(r'^account/delete', views.delete_user, name='delete_user'),
	# Navbar users page
	url(r'^users', views.users, name='users'),

    ## Place related URLS
    # Place page
    url(r'^place/(?P<place_slug>[\w\-]+)/$', views.show_place, name='show_place'),
    # Top Places page
    url(r'^top_places/$', views.top_places, name='top_places'),
    # New Places page
    url(r'^new_places/$', views.new_places, name='new_places'),
    # Popular Places page
    url(r'^popular_places/$', views.popular_places, name='popular_places'),
    # Submit place page
    url(r'^submit_place/$', views.submit_place, name='submit_place'),

    ## Trip related URLS
    # Trip page
    url(r'^trip/(?P<trip_slug>[\w\-]+)/$', views.show_trip, name='show_trip'),
    # Top Trips page
    url(r'^top_trips/$', views.top_trips, name='top_trips'),
    # New Trips page
    url(r'^new_trips/$', views.new_trips, name='new_trips'),
    # Popular Trips page
    url(r'^popular_trips/$', views.popular_trips, name='popular_trips'),
    # Submit Trip page
    url(r'^submit_trip/$', views.submit_trip, name='submit_trip'),
]
