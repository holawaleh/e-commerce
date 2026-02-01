from django.db import models

# Create your models here.
# logaccess/models.py

import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone


# ─── DOMAIN CHOICES ──────────────────────────────────────────────
# The "trades" a business owner picks at registration.
# The string on the left is what gets saved to the DB.
# The string on the right is the human-readable label.
DOMAIN_CHOICES = [
    ("hotel_tourism", "Hotel & Tourism"),
    ("pharmacy", "Pharmacy"),
    ("retail", "Retail"),
    ("agriculture", "Agriculture"),
    ("electronics", "Electronics"),
    ("fashion", "Fashion & Apparel"),
    ("food_beverage", "Food & Beverage"),
    ("auto_parts", "Automobile Parts"),
    ("technical_services", "Repairs and Technical Services"),
]


# ─── TENANT ──────────────────────────────────────────────────────
# One Tenant = one registered business = one "compound".
# domain tells us which trade they chose, which controls
# what product models and fields they see.
class Tenant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(max_length=200)
    domain = models.CharField(max_length=40, choices=DOMAIN_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.business_name} ({self.get_domain_display()})"


# ─── ROLE ────────────────────────────────────────────────────────
# Three-tier hierarchy: Owner > Manager > Staff.
# Each tenant gets one Role row per tier (created on demand).
class RoleType(models.TextChoices):
    OWNER = "owner", "Owner"
    MANAGER = "manager", "Manager"
    STAFF = "staff", "Staff"


class Role(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="roles")
    role_type = models.CharField(
        max_length=20, choices=RoleType.choices, default=RoleType.STAFF
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One of each role type per tenant — no duplicates
        unique_together = ("tenant", "role_type")
        ordering = ["role_type"]

    def __str__(self):
        return f"{self.get_role_type_display()} — {self.tenant.business_name}"


# ─── CUSTOM USER MANAGER ─────────────────────────────────────────
# Django requires a manager on any custom User model.
# create_user() handles password hashing.
# create_superuser() is for the Django admin — not tenant-bound.
class TenantUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


# ─── CUSTOM USER ─────────────────────────────────────────────────
# Replaces Django's built-in User.
# Two key additions over the default: tenant + role.
# These two fields are what make tenant isolation possible.
class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    tenant = models.ForeignKey(
        Tenant, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = TenantUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    # ── Role helpers used in ViewSets for permission checks ──
    @property
    def is_owner(self):
        return self.role and self.role.role_type == RoleType.OWNER

    @property
    def is_manager(self):
        return self.role and self.role.role_type == RoleType.MANAGER

    def has_tenant_permission(self, required_role: str) -> bool:
        """
        Returns True if the user's role is >= the required role.
        Hierarchy: owner (3) > manager (2) > staff (1).
        """
        hierarchy = {
            RoleType.OWNER: 3,
            RoleType.MANAGER: 2,
            RoleType.STAFF: 1,
        }
        if not self.role:
            return False
        return hierarchy.get(self.role.role_type, 0) >= hierarchy.get(required_role, 0)


# ─── STAFF INVITE ────────────────────────────────────────────────
# Owner creates an invite → staff clicks the link → staff registers.
# The invite binds the new user to the correct tenant and role
# without the owner ever touching a password.
class StaffInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="invites")
    email = models.EmailField()
    role_type = models.CharField(
        max_length=20, choices=RoleType.choices, default=RoleType.STAFF
    )
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_invites"
    )
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # One pending invite per email per tenant
        unique_together = ("tenant", "email")
        ordering = ["-created_at"]

    def __str__(self):
        status = "Used" if self.is_used else "Pending"
        return f"Invite to {self.email} [{status}]"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    def save(self, *args, **kwargs):
        # Default expiry: 7 days from creation
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)
