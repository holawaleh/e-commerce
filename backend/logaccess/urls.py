# logaccess/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"auth", views.AuthViewSet, basename="auth")
router.register(r"invites", views.StaffInviteViewSet, basename="invites")

urlpatterns = [
    path("", include(router.urls)),
]
