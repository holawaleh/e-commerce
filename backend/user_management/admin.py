from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Business, Role, StaffMember, Invitation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username", "first_name", "last_name", "is_staff"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["email"]


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "email", "created_at"]
    search_fields = ["name", "email"]
    list_filter = ["created_at"]


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "can_manage_inventory",
        "can_manage_sales",
        "can_manage_staff",
    ]
    list_filter = ["name"]


@admin.register(StaffMember)
class StaffMemberAdmin(admin.ModelAdmin):
    list_display = ["user", "business", "role", "is_active", "joined_at"]
    list_filter = ["role", "is_active", "joined_at"]
    search_fields = ["user__email", "business__name"]


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ["email", "business", "role", "status", "created_at", "expires_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["email", "business__name"]
