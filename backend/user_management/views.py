# user_management/views.py

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.contrib.auth import authenticate, get_user_model
from django.utils import timezone
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

from .models import Business, Role, StaffMember, Invitation
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer,
    BusinessSerializer,
    RoleSerializer,
    StaffMemberSerializer,
    StaffMemberDetailSerializer,
    InvitationSerializer,
    AcceptInvitationSerializer,
    CreateInvitationSerializer,
    UpdateStaffRoleSerializer,
)
from .permissions import IsBusinessOwner, CanManageStaff

User = get_user_model()

# ============= Authentication Views =============


class RegisterView(generics.CreateAPIView):
    """Register a new user"""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "message": "User registered successfully",
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Login user and return JWT tokens"""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Authenticate user
        user = authenticate(username=email, password=password)

        if user is None:
            return Response(
                {"error": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": "User account is disabled"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        # Get user's businesses
        businesses = Business.objects.filter(
            Q(owner=user) | Q(staff_members__user=user, staff_members__is_active=True)
        ).distinct()

        return Response(
            {
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "businesses": BusinessSerializer(businesses, many=True).data,
                "message": "Login successful",
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """Logout user by blacklisting refresh token"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CurrentUserView(APIView):
    """Get current authenticated user details"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get user's businesses and roles
        staff_memberships = StaffMember.objects.filter(
            user=user, is_active=True
        ).select_related("business", "role")

        businesses_data = []
        for membership in staff_memberships:
            businesses_data.append(
                {
                    "business": BusinessSerializer(membership.business).data,
                    "role": RoleSerializer(membership.role).data,
                    "is_owner": membership.business.owner == user,
                }
            )

        return Response(
            {"user": UserSerializer(user).data, "businesses": businesses_data}
        )


# ============= Business Views =============


class BusinessViewSet(viewsets.ModelViewSet):
    """CRUD operations for businesses"""

    serializer_class = BusinessSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return businesses where user is owner or staff member
        return Business.objects.filter(
            Q(owner=self.request.user)
            | Q(staff_members__user=self.request.user, staff_members__is_active=True)
        ).distinct()

    def perform_create(self, serializer):
        # Create business and automatically add owner as staff with OWNER role
        business = serializer.save(owner=self.request.user)

        # Get OWNER role
        owner_role = Role.objects.get(name=Role.OWNER)

        # Add owner as staff member
        StaffMember.objects.create(
            user=self.request.user,
            business=business,
            role=owner_role,
            invited_by=self.request.user,
        )

    @action(detail=True, methods=["get"])
    def staff(self, request, pk=None):
        """Get all staff members for a business"""
        business = self.get_object()
        staff_members = StaffMember.objects.filter(
            business=business, is_active=True
        ).select_related("user", "role", "invited_by")

        serializer = StaffMemberDetailSerializer(staff_members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def my_role(self, request, pk=None):
        """Get current user's role in this business"""
        business = self.get_object()

        try:
            staff_member = StaffMember.objects.get(
                user=request.user, business=business, is_active=True
            )
            return Response(
                {
                    "role": RoleSerializer(staff_member.role).data,
                    "is_owner": business.owner == request.user,
                    "permissions": {
                        "can_manage_inventory": staff_member.role.can_manage_inventory,
                        "can_manage_sales": staff_member.role.can_manage_sales,
                        "can_manage_services": staff_member.role.can_manage_sales,  # Same as sales
                        "can_view_reports": staff_member.role.can_view_reports,
                        "can_manage_staff": staff_member.role.can_manage_staff,
                        "can_manage_settings": staff_member.role.can_manage_settings,
                    },
                }
            )
        except StaffMember.DoesNotExist:
            return Response(
                {"error": "You are not a member of this business"},
                status=status.HTTP_404_NOT_FOUND,
            )


# ============= Invitation Views =============


class InvitationViewSet(viewsets.ModelViewSet):
    """CRUD operations for staff invitations"""

    serializer_class = InvitationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get invitations for businesses where user can manage staff
        user_businesses = Business.objects.filter(
            Q(owner=self.request.user)
            | Q(
                staff_members__user=self.request.user,
                staff_members__role__can_manage_staff=True,
                staff_members__is_active=True,
            )
        ).distinct()

        return Invitation.objects.filter(business__in=user_businesses).select_related(
            "business", "role", "invited_by"
        )

    def create(self, request, *args, **kwargs):
        """Create a new invitation"""
        business_id = request.data.get("business")

        # Verify user can manage staff for this business
        try:
            business = Business.objects.get(id=business_id)

            # Check if owner or has permission
            if business.owner != request.user:
                staff_member = StaffMember.objects.get(
                    user=request.user, business=business, is_active=True
                )
                if not staff_member.role.can_manage_staff:
                    return Response(
                        {"error": "You do not have permission to invite staff"},
                        status=status.HTTP_403_FORBIDDEN,
                    )
        except (Business.DoesNotExist, StaffMember.DoesNotExist):
            return Response(
                {"error": "Business not found or access denied"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        invitation = serializer.save()

        return Response(
            {
                "invitation": InvitationSerializer(invitation).data,
                "message": "Invitation sent successfully",
                "invitation_link": f"http://localhost:3000/accept-invitation/{invitation.token}",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def accept(self, request):
        """Accept an invitation"""
        serializer = AcceptInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            invitation = Invitation.objects.select_related(
                "business", "role", "invited_by"
            ).get(token=token)

            if not invitation.is_valid():
                return Response(
                    {"error": "Invitation is invalid or expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if user email matches invitation
            if request.user.email != invitation.email:
                return Response(
                    {"error": "This invitation is not for your email address"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Check if already a staff member
            if StaffMember.objects.filter(
                user=request.user, business=invitation.business
            ).exists():
                return Response(
                    {"error": "You are already a member of this business"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create staff member
            staff_member = StaffMember.objects.create(
                user=request.user,
                business=invitation.business,
                role=invitation.role,
                invited_by=invitation.invited_by,
            )

            # Update invitation status
            invitation.status = Invitation.ACCEPTED
            invitation.accepted_at = timezone.now()
            invitation.save()

            return Response(
                {
                    "message": "Invitation accepted successfully",
                    "business": BusinessSerializer(invitation.business).data,
                    "role": RoleSerializer(invitation.role).data,
                },
                status=status.HTTP_200_OK,
            )

        except Invitation.DoesNotExist:
            return Response(
                {"error": "Invitation not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"])
    def resend(self, request, pk=None):
        """Resend an invitation"""
        invitation = self.get_object()

        if invitation.status != Invitation.PENDING:
            return Response(
                {"error": "Can only resend pending invitations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update expiration
        invitation.expires_at = timezone.now() + timedelta(days=7)
        invitation.save()

        return Response(
            {
                "message": "Invitation resent successfully",
                "invitation": InvitationSerializer(invitation).data,
            }
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a pending invitation"""
        invitation = self.get_object()

        if invitation.status != Invitation.PENDING:
            return Response(
                {"error": "Can only cancel pending invitations"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.status = Invitation.EXPIRED
        invitation.save()

        return Response({"message": "Invitation cancelled successfully"})


# ============= Staff Management Views =============


class StaffMemberViewSet(viewsets.ModelViewSet):
    """Manage staff members"""

    serializer_class = StaffMemberDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get staff for businesses where user has management permission
        user_businesses = Business.objects.filter(
            Q(owner=self.request.user)
            | Q(
                staff_members__user=self.request.user,
                staff_members__role__can_manage_staff=True,
                staff_members__is_active=True,
            )
        ).distinct()

        return StaffMember.objects.filter(business__in=user_businesses).select_related(
            "user", "business", "role", "invited_by"
        )

    @action(detail=True, methods=["patch"])
    def update_role(self, request, pk=None):
        """Update staff member's role"""
        staff_member = self.get_object()

        # Prevent changing owner's role
        if staff_member.business.owner == staff_member.user:
            return Response(
                {"error": "Cannot change owner's role"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = UpdateStaffRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = serializer.validated_data["role_id"]

        try:
            role = Role.objects.get(id=role_id)

            # Prevent assigning OWNER role
            if role.name == Role.OWNER:
                return Response(
                    {"error": "Cannot assign OWNER role to staff members"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            staff_member.role = role
            staff_member.save()

            return Response(
                {
                    "message": "Role updated successfully",
                    "staff_member": StaffMemberDetailSerializer(staff_member).data,
                }
            )

        except Role.DoesNotExist:
            return Response(
                {"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        """Deactivate a staff member"""
        staff_member = self.get_object()

        # Prevent deactivating owner
        if staff_member.business.owner == staff_member.user:
            return Response(
                {"error": "Cannot deactivate business owner"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        staff_member.is_active = False
        staff_member.save()

        return Response({"message": "Staff member deactivated successfully"})

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Reactivate a staff member"""
        staff_member = self.get_object()

        staff_member.is_active = True
        staff_member.save()

        return Response({"message": "Staff member activated successfully"})


# ============= Role Views =============


class RoleViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only viewset for roles"""

    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Exclude OWNER role from being assigned
        return Role.objects.exclude(name=Role.OWNER)
