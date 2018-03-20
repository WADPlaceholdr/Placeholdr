from django.conf.urls import url
from placeholdr import views


urlpatterns = [
	# Index page
	url(r'^$', views.index, name='index'),
	# About page
	url(r'^about/', views.about, name='about'),
	# Trip page
	url(r'^trip/(?P<trip_slug>[\w\-]+)/$', views.show_trip, name='show_trip'),
	# Place page
	url(r'^place/(?P<place_slug>[\w\-]+)/$', views.show_place, name='show_place'),
	# User page
	url(r'^user/(?P<username>\w+)/$', views.show_user, name='show_user'),
	# Team page
	url(r'^team/', views.team, name='team'),
	#Contact page
	url(r'^contact-us/', views.contact, name='contact'),
	#Help page
	url(r'^help/', views.help, name='help'),
	# Register page
	url(r'^register/$', views.register, name='register'),
	# Login page
	url(r'^login/$', views.user_login, name='login'),
	# Restricted page
	url(r'^restricted/', views.restricted, name='restricted'),
	# Delete account page
	url(r'^account/edit', views.edit_profile, name='edit_profile'),
	# Delete account page
	url(r'^account/delete', views.delete_user, name='delete_user'),
	# Account page
	url(r'^account/$', views.show_account, name='account'),
	# logout page
	url(r'^logout/$', views.user_logout, name='logout'),
	# search results page
	url(r'^search/$', views.search, name='search'),
	# Ajax page
	url(r'^ajax/$', views.ajax_tasks, name='ajax_tasks'),
	# Top Places page
	url(r'^top_places/$', views.top_places, name='top_places'),
	# New Places page
	url(r'^new_places/$', views.new_places, name='new_places'),
	# Popular Places page
	url(r'^popular_places/$', views.popular_places, name='popular_places'),
	# Top Trips page
	url(r'^top_trips/$', views.top_trips, name='top_trips'),
	# New Trips page
	url(r'^new_trips/$', views.new_trips, name='new_trips'),
	# Popular Trips page
	url(r'^popular_trips/$', views.popular_trips, name='popular_trips'),
]