# logaccess/serializers.py

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Tenant, User, Role, RoleType, StaffInvite, DOMAIN_CHOICES


# ─── OWNER REGISTRATION ──────────────────────────────────────────
# Flow: user fills form → this serializer validates → .save() creates
# Tenant + Owner Role + User in one go.
class OwnerRegistrationSerializer(serializers.Serializer):
    # Business fields
    business_name = serializers.CharField(max_length=200)
    domain = serializers.ChoiceField(choices=DOMAIN_CHOICES)
    # Personal fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100, required=False, default="")
    last_name = serializers.CharField(max_length=100, required=False, default="")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        # Step 1 — create the compound
        tenant = Tenant.objects.create(
            business_name=validated_data["business_name"],
            domain=validated_data["domain"],
        )
        # Step 2 — create the owner role for that compound
        owner_role = Role.objects.create(
            tenant=tenant,
            role_type=RoleType.OWNER,
            description="Business owner — full access",
        )
        # Step 3 — create the user, tied to both
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            tenant=tenant,
            role=owner_role,
        )
        return user


# ─── STAFF REGISTRATION (via invite token) ──────────────────────
# Staff don't choose a domain — the invite already knows the tenant + role.
class StaffRegistrationSerializer(serializers.Serializer):
    invite_token = serializers.UUIDField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=100, required=False, default="")
    last_name = serializers.CharField(max_length=100, required=False, default="")

    def validate_invite_token(self, value):
        try:
            self.invite = StaffInvite.objects.get(id=value)
        except StaffInvite.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired invite token.")
        if self.invite.is_used:
            raise serializers.ValidationError("This invite has already been used.")
        if self.invite.is_expired:
            raise serializers.ValidationError("This invite has expired.")
        return value

    def validate_email(self, value):
        if hasattr(self, "invite") and self.invite.email != value:
            raise serializers.ValidationError("Email does not match the invite.")
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        invite = self.invite
        tenant = invite.tenant

        # Get or create the role row for this role_type on this tenant
        role, _ = Role.objects.get_or_create(
            tenant=tenant,
            role_type=invite.role_type,
            defaults={"description": f"{invite.get_role_type_display()} level access"},
        )

        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            tenant=tenant,
            role=role,
        )

        # Mark invite consumed so it can't be reused
        invite.is_used = True
        invite.save()

        return user


# ─── LOGIN ───────────────────────────────────────────────────────
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


# ─── STAFF INVITE (created by owner/manager) ─────────────────────
class StaffInviteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffInvite
        fields = ["id", "email", "role_type", "expires_at", "created_at", "is_used"]
        read_only_fields = ["id", "created_at", "is_used"]

    def validate_role_type(self, value):
        user = self.context["request"].user
        if value == RoleType.OWNER:
            raise serializers.ValidationError("Cannot invite an owner.")
        if value == RoleType.MANAGER and not user.is_owner:
            raise serializers.ValidationError("Only the owner can invite managers.")
        return value

    def validate_email(self, value):
        tenant = self.context["request"].user.tenant
        if StaffInvite.objects.filter(
            tenant=tenant, email=value, is_used=False
        ).exists():
            raise serializers.ValidationError(
                "An active invite for this email already exists."
            )
        return value

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data["tenant"] = user.tenant
        validated_data["invited_by"] = user
        if "expires_at" not in validated_data:
            validated_data["expires_at"] = timezone.now() + timedelta(days=7)
        return super().create(validated_data)


# ─── READ SERIALIZERS (shape API responses) ─────────────────────
class TenantReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ["id", "business_name", "domain", "created_at"]


class UserReadSerializer(serializers.ModelSerializer):
    tenant = TenantReadSerializer(read_only=True)
    role = serializers.CharField(source="role.get_role_type_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "tenant",
            "role",
            "date_joined",
        ]


class StaffInviteReadSerializer(serializers.ModelSerializer):
    invited_by = serializers.EmailField(source="invited_by.email", read_only=True)

    class Meta:
        model = StaffInvite
        fields = [
            "id",
            "email",
            "role_type",
            "invited_by",
            "is_used",
            "expires_at",
            "created_at",
        ]
