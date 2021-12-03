from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.information, name='information'),
    path('document', views.document, name='document'),
    path('update_documents', views.update_documents, name="update_documents"),
    path('update_units', views.update_units, name="update_units")
]