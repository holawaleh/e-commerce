# logaccess/views.py

from django.contrib.auth import authenticate
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import StaffInvite, RoleType
from .serializers import (
    OwnerRegistrationSerializer,
    StaffRegistrationSerializer,
    LoginSerializer,
    StaffInviteCreateSerializer,
    StaffInviteReadSerializer,
    UserReadSerializer,
)


# ─── TENANT SCOPING MIXIN ────────────────────────────────────────
# This is the line that keeps tenants isolated.
# Import and use this in inventory/views.py and sales/views.py.
# It overrides get_queryset() so it ONLY returns rows belonging
# to the authenticated user's tenant.
class TenantScopedPermission:
    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user and self.request.user.tenant:
            return qs.filter(tenant=self.request.user.tenant)
        return qs.none()  # No tenant → empty result. Safe default.


# ─── AUTH VIEWSET ────────────────────────────────────────────────
# Handles registration (owner + staff), login, and "who am I".
# All endpoints here are public (no token needed) except /me/.
class AuthViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    # POST /api/auth/register-owner/
    @action(detail=False, methods=["post"], url_path="register-owner")
    def register_owner(self, request):
        serializer = OwnerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = self._get_tokens(user)
        return Response(
            {
                "message": "Registration successful.",
                "user": UserReadSerializer(user).data,
                **tokens,
            },
            status=status.HTTP_201_CREATED,
        )

    # POST /api/auth/register-staff/
    @action(detail=False, methods=["post"], url_path="register-staff")
    def register_staff(self, request):
        serializer = StaffRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = self._get_tokens(user)
        return Response(
            {
                "message": "Staff registration successful.",
                "user": UserReadSerializer(user).data,
                **tokens,
            },
            status=status.HTTP_201_CREATED,
        )

    # POST /api/auth/login/
    @action(detail=False, methods=["post"])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.is_active:
            return Response(
                {"error": "Account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = self._get_tokens(user)
        return Response(
            {
                "message": "Login successful.",
                "user": UserReadSerializer(user).data,
                **tokens,
            },
        )

    # GET /api/auth/me/
    # Returns the logged-in user's full profile including tenant info
    @action(
        detail=False,
        methods=["get"],
        url_path="me",
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        return Response(UserReadSerializer(request.user).data)

    # ── Helper: generate JWT access + refresh tokens ──
    @staticmethod
    def _get_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }


# ─── STAFF INVITE VIEWSET ────────────────────────────────────────
# CRUD for invites — scoped to the user's tenant.
# Only owner/manager can list or create. Only owner can delete.
class StaffInviteViewSet(TenantScopedPermission, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StaffInviteReadSerializer
    queryset = StaffInvite.objects.all()

    # GET /api/invites/
    def list(self, request, *args, **kwargs):
        if not request.user.has_tenant_permission(RoleType.MANAGER):
            return Response(
                {"error": "You don't have permission to view invites."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)

    # POST /api/invites/
    def create(self, request, *args, **kwargs):
        if not request.user.has_tenant_permission(RoleType.MANAGER):
            return Response(
                {"error": "Only owners or managers can create invites."},
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = StaffInviteCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        invite = serializer.save()
        return Response(
            StaffInviteReadSerializer(invite).data,
            status=status.HTTP_201_CREATED,
        )

    # DELETE /api/invites/{id}/
    def destroy(self, request, *args, **kwargs):
        if not request.user.is_owner:
            return Response(
                {"error": "Only the owner can delete invites."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)

    # Invites are immutable once created — block PUT and PATCH
    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "Invites cannot be updated."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
