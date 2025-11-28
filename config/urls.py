from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('mailings/', include('mailings.urls', namespace='mailings')),
]