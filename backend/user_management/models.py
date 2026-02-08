from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    """Extended User model"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    # Make email the username field
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email


class Business(models.Model):
    """Business/Organization model"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_businesses"
    )
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "businesses"
        verbose_name_plural = "Businesses"

    def __str__(self):
        return self.name


class Role(models.Model):
    """User roles for permission management"""

    OWNER = "OWNER"
    MANAGER = "MANAGER"
    SALES_STAFF = "SALES_STAFF"
    INVENTORY_STAFF = "INVENTORY_STAFF"

    ROLE_CHOICES = [
        (OWNER, "Owner"),
        (MANAGER, "Manager"),
        (SALES_STAFF, "Sales Staff"),  # This role also covers services
        (INVENTORY_STAFF, "Inventory Staff"),
    ]

    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True)

    # Permissions
    can_manage_inventory = models.BooleanField(default=False)
    can_manage_sales = models.BooleanField(default=False)
    # Note: can_manage_sales also grants access to services module
    can_view_reports = models.BooleanField(default=False)
    can_manage_staff = models.BooleanField(default=False)
    can_manage_settings = models.BooleanField(default=False)

    class Meta:
        db_table = "roles"

    def __str__(self):
        return self.get_name_display()

    @property
    def can_manage_services(self):
        """Services access is tied to sales permissions"""
        return self.can_manage_sales


class StaffMember(models.Model):
    """Link users to businesses with roles"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="staff_memberships"
    )
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="staff_members"
    )
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)
    invited_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="invited_staff"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "staff_members"
        unique_together = ["user", "business"]

    def __str__(self):
        return f"{self.user.email} - {self.business.name} ({self.role.name})"

    @property
    def can_manage_services(self):
        """Helper property for services access"""
        return self.role.can_manage_sales


class Invitation(models.Model):
    """Staff invitation system"""

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"

    STATUS_CHOICES = [
        (PENDING, "Pending"),
        (ACCEPTED, "Accepted"),
        (REJECTED, "Rejected"),
        (EXPIRED, "Expired"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, related_name="invitations"
    )
    email = models.EmailField()
    role = models.ForeignKey(Role, on_delete=models.PROTECT)
    invited_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_invitations"
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invitations"
        unique_together = ["business", "email", "status"]

    def __str__(self):
        return f"Invitation to {self.email} for {self.business.name}"

    def is_valid(self):
        from django.utils import timezone

        return self.status == self.PENDING and self.expires_at > timezone.now()
