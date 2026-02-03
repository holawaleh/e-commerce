# Generated migration: Multi-domain support and time-less staff invites

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "logaccess",
            "0001_initial",
        ),  # Adjust this if your initial migration has a different name
    ]

    operations = [
        # Create the new Domain model
        migrations.CreateModel(
            name="Domain",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        choices=[
                            ("hotel_tourism", "Hotel & Tourism"),
                            ("pharmacy", "Pharmacy"),
                            ("retail", "Retail"),
                            ("agriculture", "Agriculture"),
                            ("electronics", "Electronics"),
                            ("fashion", "Fashion & Apparel"),
                            ("food_beverage", "Food & Beverage"),
                            ("auto_parts", "Automobile Parts"),
                            ("technical_services", "Repairs and Technical Services"),
                        ],
                        max_length=40,
                        unique=True,
                    ),
                ),
                ("label", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["code"],
            },
        ),
        # Remove old domain field from Tenant
        migrations.RemoveField(
            model_name="tenant",
            name="domain",
        ),
        # Add primary_domain FK to Tenant
        migrations.AddField(
            model_name="tenant",
            name="primary_domain",
            field=models.ForeignKey(
                blank=True,
                help_text="Default domain for product creation",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="primary_for_tenants",
                to="logaccess.domain",
            ),
        ),
        # Add M2M domains to Tenant
        migrations.AddField(
            model_name="tenant",
            name="domains",
            field=models.ManyToManyField(
                help_text="Business domains/trades",
                related_name="tenants",
                to="logaccess.domain",
            ),
        ),
        # Remove expires_at from StaffInvite
        migrations.RemoveField(
            model_name="staffinvite",
            name="expires_at",
        ),
    ]
