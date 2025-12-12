from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("mailings/", include("mailings.urls", namespace="mailings")),
    path("users/", include("users.urls", namespace="users")),
]
