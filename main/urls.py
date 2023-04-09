from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("attractions/<int:id>", views.attractions, name="attractions"),
    path("plans", views.plans, name="plans"),
    path("intro", views.intro, name="intro"),
]
