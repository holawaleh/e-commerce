from rest_framework import permissions
from .models import StaffMember


class IsBusinessOwner(permissions.BasePermission):
    """Check if user is the owner of the business"""

    def has_object_permission(self, request, view, obj):
        # obj is a Business instance
        return obj.owner == request.user


class IsBusinessStaff(permissions.BasePermission):
    """Check if user is staff member of the business"""

    def has_object_permission(self, request, view, obj):
        # obj is a Business instance
        return StaffMember.objects.filter(
            user=request.user, business=obj, is_active=True
        ).exists()


class CanManageStaff(permissions.BasePermission):
    """Check if user has permission to manage staff"""

    def has_permission(self, request, view):
        # Get business from request data or query params
        business_id = request.data.get("business") or request.query_params.get(
            "business"
        )

        if not business_id:
            return False

        try:
            staff_member = StaffMember.objects.get(
                user=request.user, business_id=business_id, is_active=True
            )
            return staff_member.role.can_manage_staff
        except StaffMember.DoesNotExist:
            return False


class HasBusinessPermission(permissions.BasePermission):
    """
    Generic permission checker based on role permissions
    Usage: Set permission_required in view
    """

    def has_permission(self, request, view):
        permission_required = getattr(view, "permission_required", None)

        if not permission_required:
            return True

        business_id = request.data.get("business") or request.query_params.get(
            "business"
        )

        if not business_id:
            return False

        try:
            staff_member = StaffMember.objects.get(
                user=request.user, business_id=business_id, is_active=True
            )

            # Handle services permission check
            if permission_required == "can_manage_services":
                return (
                    staff_member.role.can_manage_sales
                )  # Sales permission includes services

            return getattr(staff_member.role, permission_required, False)
        except StaffMember.DoesNotExist:
            return False


class CanManageSales(permissions.BasePermission):
    """Check if user can manage sales (also grants services access)"""

    def has_permission(self, request, view):
        business_id = request.data.get("business") or request.query_params.get(
            "business"
        )

        if not business_id:
            return False

        try:
            staff_member = StaffMember.objects.get(
                user=request.user, business_id=business_id, is_active=True
            )
            return staff_member.role.can_manage_sales
        except StaffMember.DoesNotExist:
            return False


# Alias for services - same as sales permission
CanManageServices = CanManageSales


class CanManageInventory(permissions.BasePermission):
    """Check if user can manage inventory"""

    def has_permission(self, request, view):
        business_id = request.data.get("business") or request.query_params.get(
            "business"
        )

        if not business_id:
            return False

        try:
            staff_member = StaffMember.objects.get(
                user=request.user, business_id=business_id, is_active=True
            )
            return staff_member.role.can_manage_inventory
        except StaffMember.DoesNotExist:
            return False
