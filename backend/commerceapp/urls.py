# commerceapp/urls.py

from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # JWT token refresh endpoint
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # App routes
    path("api/", include("logaccess.urls")),  # auth + invites
    path("api/inventory/", include("inventory.urls")),  # products
    path("api/sales/", include("sales.urls")),  # orders
]
