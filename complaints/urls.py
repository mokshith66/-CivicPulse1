from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("health/", views.health, name="health"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("admin/login/", views.admin_login, name="admin_login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("complaints/new/", views.new_complaint, name="new_complaint"),
    path("complaints/", views.my_complaints, name="my_complaints"),
    path("complaints/<str:complaint_id>/", views.complaint_detail, name="complaint_detail"),
    path("track/", views.track, name="track"),
    path("uploads/<path:filename>", views.uploaded_file, name="uploaded_file"),
    path("map/", views.complaint_map, name="complaint_map"),
    path("profile/", views.profile, name="profile"),
    path("admin/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/complaints/", views.admin_complaints, name="admin_complaints"),
    path("admin/complaints/<str:complaint_id>/", views.admin_complaint_detail, name="admin_complaint_detail"),
    path("admin/complaints/<str:complaint_id>/delete/", views.delete_complaint, name="delete_complaint"),
    path("admin/analytics/", views.analytics, name="analytics"),
]
