from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('message', views.message, name='message'),
    path('site', views.site, name='site'),
    path('location/<str:zuser_id>', views.location, name='location'),
    path('location_confirm', views.location_confirm, name='location_confirm'),
    path('declare_confirm', views.declare_confirm, name='declare_confirm'),
    path('checkpoint_confirm', views.checkpoint_confirm, name='checkpoint_confirm'),
    path('follow_hook', views.follow_hook, name='follow_hook')
]