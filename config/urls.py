from django.contrib import admin
from django.urls import include, path

handler403 = "complaints.views.forbidden"
handler404 = "complaints.views.not_found"
handler500 = "complaints.views.server_error"

urlpatterns = [
    # Built-in Django admin (database browser) lives on its own path so it never
    # clashes with CivicPulse's own /admin/... administrator pages.
    path("django-admin/", admin.site.urls),
    path("", include("complaints.urls")),
]
