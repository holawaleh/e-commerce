from django.core.management.base import BaseCommand
from user_management.models import Role


class Command(BaseCommand):
    help = "Create default roles"

    def handle(self, *args, **kwargs):
        roles = [
            {
                "name": Role.OWNER,
                "description": "Business owner with full access",
                "can_manage_inventory": True,
                "can_manage_sales": True,  # Also grants services access
                "can_view_reports": True,
                "can_manage_staff": True,
                "can_manage_settings": True,
            },
            {
                "name": Role.MANAGER,
                "description": "Manager with most permissions (includes sales and services)",
                "can_manage_inventory": True,
                "can_manage_sales": True,  # Also grants services access
                "can_view_reports": True,
                "can_manage_staff": True,
                "can_manage_settings": False,
            },
            {
                "name": Role.SALES_STAFF,
                "description": "Sales and Services staff with POS and service booking access",
                "can_manage_inventory": False,
                "can_manage_sales": True,  # Also grants services access
                "can_view_reports": False,
                "can_manage_staff": False,
                "can_manage_settings": False,
            },
            {
                "name": Role.INVENTORY_STAFF,
                "description": "Inventory staff with stock management access only",
                "can_manage_inventory": True,
                "can_manage_sales": False,  # No sales or services access
                "can_view_reports": False,
                "can_manage_staff": False,
                "can_manage_settings": False,
            },
        ]

        for role_data in roles:
            role, created = Role.objects.get_or_create(
                name=role_data["name"], defaults=role_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created role: {role.get_name_display()}")
                )
            else:
                # Update existing role with new description
                for key, value in role_data.items():
                    setattr(role, key, value)
                role.save()
                self.stdout.write(
                    self.style.WARNING(f"Updated role: {role.get_name_display()}")
                )

        self.stdout.write(
            self.style.SUCCESS("\n✓ All roles created/updated successfully!")
        )
        self.stdout.write(
            self.style.SUCCESS(
                "Note: Sales Staff role now includes access to Services module"
            )
        )
