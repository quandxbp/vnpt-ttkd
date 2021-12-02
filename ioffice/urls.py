from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.information, name='information'),
    path('document', views.document, name='document'),
]