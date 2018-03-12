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
]