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
    url(r'^user/(?P<user_id>[\w\-]+)/$', views.show_user, name='show_user'),
    # Register page
    url(r'^register/$', views.register, name='register'),
    # Login page
    url(r'^login/$', views.user_login, name='login'),
    # Restricted page
    url(r'^restricted/', views.restricted, name='restricted'),
    # logout page
    url(r'^logout/$', views.user_logout, name='logout'),
]
