from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Business, Role, StaffMember, Invitation
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "phone"]
        read_only_fields = ["id"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
        ]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "Passwords don't match"})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class BusinessSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    staff_count = serializers.SerializerMethodField()

    class Meta:
        model = Business
        fields = [
            "id",
            "name",
            "owner",
            "address",
            "phone",
            "email",
            "staff_count",
            "created_at",
        ]
        read_only_fields = ["id", "owner", "created_at"]

    def get_staff_count(self, obj):
        return obj.staff_members.filter(is_active=True).count()


class RoleSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="get_name_display", read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "can_manage_inventory",
            "can_manage_sales",
            "can_view_reports",
            "can_manage_staff",
            "can_manage_settings",
        ]


class StaffMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    role_name = serializers.CharField(source="role.get_name_display", read_only=True)

    class Meta:
        model = StaffMember
        fields = ["id", "user", "role", "role_name", "is_active", "joined_at"]
        read_only_fields = ["id", "joined_at"]


class StaffMemberDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    role = RoleSerializer(read_only=True)
    business = BusinessSerializer(read_only=True)
    invited_by = UserSerializer(read_only=True)

    class Meta:
        model = StaffMember
        fields = [
            "id",
            "user",
            "business",
            "role",
            "is_active",
            "invited_by",
            "joined_at",
        ]
        read_only_fields = ["id", "invited_by", "joined_at"]


class InvitationSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(source="business.name", read_only=True)
    role_name = serializers.CharField(source="role.get_name_display", read_only=True)
    invited_by_name = serializers.SerializerMethodField()
    is_valid = serializers.SerializerMethodField()

    class Meta:
        model = Invitation
        fields = [
            "id",
            "email",
            "business",
            "business_name",
            "role",
            "role_name",
            "invited_by_name",
            "status",
            "is_valid",
            "created_at",
            "expires_at",
        ]
        read_only_fields = [
            "id",
            "status",
            "created_at",
            "expires_at",
            "invited_by_name",
            "is_valid",
        ]

    def get_invited_by_name(self, obj):
        return (
            f"{obj.invited_by.first_name} {obj.invited_by.last_name}"
            if obj.invited_by.first_name
            else obj.invited_by.email
        )

    def get_is_valid(self, obj):
        return obj.is_valid()

    def validate(self, data):
        email = data.get("email")
        business = data.get("business")

        # Check if user already exists and is already staff
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            if StaffMember.objects.filter(user=user, business=business).exists():
                raise serializers.ValidationError(
                    {"email": "User is already a staff member"}
                )

        # Check for pending invitation
        if Invitation.objects.filter(
            email=email, business=business, status=Invitation.PENDING
        ).exists():
            raise serializers.ValidationError(
                {"email": "Pending invitation already exists"}
            )

        return data

    def create(self, validated_data):
        # Set expiration to 7 days from now
        validated_data["expires_at"] = timezone.now() + timedelta(days=7)
        validated_data["invited_by"] = self.context["request"].user

        invitation = super().create(validated_data)

        # TODO: Send email with invitation link
        # send_invitation_email(invitation)

        return invitation


class CreateInvitationSerializer(serializers.Serializer):
    """Simplified serializer for creating invitations"""

    email = serializers.EmailField()
    role_id = serializers.UUIDField()

    def validate_email(self, value):
        return value.lower()


class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class UpdateStaffRoleSerializer(serializers.Serializer):
    """Serializer for updating staff member role"""

    role_id = serializers.UUIDField()

    def validate_role_id(self, value):
        try:
            Role.objects.get(id=value)
        except Role.DoesNotExist:
            raise serializers.ValidationError("Role does not exist")
        return value


class RoleSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="get_name_display", read_only=True)
    can_manage_services = serializers.BooleanField(read_only=True)  # Add this property

    class Meta:
        model = Role
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "can_manage_inventory",
            "can_manage_sales",
            "can_manage_services",
            "can_view_reports",
            "can_manage_staff",
            "can_manage_settings",
        ]
