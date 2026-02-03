# logaccess/serializers.py

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import Tenant, User, Role, RoleType, StaffInvite, DOMAIN_CHOICES, Domain


# ─── OWNER REGISTRATION ──────────────────────────────────────────
# Flow: user fills form → this serializer validates → .save() creates
# Tenant + Owner Role + User in one go.
# Owner can now select multiple domains.
class OwnerRegistrationSerializer(serializers.Serializer):
    # Business fields
    business_name = serializers.CharField(max_length=200)
    domain_codes = serializers.ListField(
        child=serializers.ChoiceField(choices=[c[0] for c in DOMAIN_CHOICES]),
        help_text="List of domain codes (e.g., ['pharmacy', 'retail'])",
    )
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

    def validate_domain_codes(self, value):
        if not value:
            raise serializers.ValidationError("At least one domain must be selected.")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Duplicate domains are not allowed.")
        return value

    def create(self, validated_data):
        # Step 1 — create the tenant
        tenant = Tenant.objects.create(
            business_name=validated_data["business_name"],
        )

        # Step 2 — get or create Domain objects and assign to tenant
        domain_codes = validated_data["domain_codes"]
        for code in domain_codes:
            domain, _ = Domain.objects.get_or_create(code=code)
            tenant.domains.add(domain)

        # Step 3 — set primary domain (first one)
        tenant.primary_domain = tenant.domains.first()
        tenant.save()

        # Step 4 — create the owner role for this tenant
        owner_role = Role.objects.create(
            tenant=tenant,
            role_type=RoleType.OWNER,
            description="Business owner — full access",
        )

        # Step 5 — create the user, tied to both
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
            raise serializers.ValidationError("Invalid invite token.")
        if self.invite.is_used:
            raise serializers.ValidationError("This invite has already been used.")
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
        fields = ["id", "email", "role_type", "created_at", "is_used"]
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
        return super().create(validated_data)


# ─── READ SERIALIZERS (shape API responses) ─────────────────────
class TenantReadSerializer(serializers.ModelSerializer):
    domains = serializers.StringRelatedField(many=True, read_only=True)
    primary_domain = serializers.CharField(
        source="primary_domain.code", read_only=True, allow_null=True
    )

    class Meta:
        model = Tenant
        fields = ["id", "business_name", "domains", "primary_domain", "created_at"]


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
            "created_at",
        ]
