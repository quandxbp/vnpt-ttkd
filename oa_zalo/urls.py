from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('zalo_base.urls')),
    path('ioffice/', include('ioffice.urls')),
    path('admin/', admin.site.urls),
]

import execute