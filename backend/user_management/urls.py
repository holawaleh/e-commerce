# user_management/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    BusinessViewSet,
    InvitationViewSet,
    StaffMemberViewSet,
    RoleViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r"businesses", BusinessViewSet, basename="business")
router.register(r"invitations", InvitationViewSet, basename="invitation")
router.register(r"staff", StaffMemberViewSet, basename="staff")
router.register(r"roles", RoleViewSet, basename="role")

urlpatterns = [
    # Authentication endpoints
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/me/", CurrentUserView.as_view(), name="current_user"),
    # Router URLs (businesses, invitations, staff, roles)
    path("", include(router.urls)),
]
