from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("cabinet/", views.cabinet_view, name="cabinet"),
    path("booking/", views.booking_create_view, name="booking"),
    path("review/<int:booking_id>/", views.review_create_view, name="review"),
    path("admin/login/", views.AdminLoginView.as_view(), name="admin_login"),
    path("admin/logout/", views.AdminLogoutView.as_view(), name="admin_logout"),
    path("admin/", views.admin_panel_view, name="admin_panel"),
]
