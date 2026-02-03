# e-commerce

**E‑commerce micro‑service (Django + DRF)** ✅

A multi‑tenant commerce backend designed for small-to-medium businesses. It provides tenant-scoped authentication, staff invitation flows, product management (domain-specific product models & serializers), and order/sales management.

---

## 🔧 Quick start

1. Create & activate a Python virtual environment:

```bash
python -m venv comenv
# Windows
comenv\Scripts\activate
# macOS / Linux
source comenv/bin/activate
```

1. Install dependencies (if you have a `requirements.txt`):

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt`, install the usual packages:

```bash
pip install django djangorestframework djangorestframework-simplejwt pillow
```

1. Create DB and run migrations:

```bash
python manage.py migrate
```

1. Create a superuser (optional):

```bash
python manage.py createsuperuser
```

1. Run the dev server:

```bash
python manage.py runserver
```

---

## 📁 Project structure (important apps)

- `commerceapp` — project settings & root `urls.py` (`/api/` mounted here).
- `logaccess` — tenant, user, auth flows, staff invites.
- `inventory` — product management (dynamic serializers & models by tenant domain).
- `sales` — orders and line items.
- `domains` — domain-specific product models used by `inventory`.

---

## � Key changes (v2)

✅ **Multi-domain support:** A company can now manage multiple domains (e.g., pharmacy + retail). Choose one or more at registration.  
✅ **Staff management (owner-controlled):** No time limits on invites. Owner can remove staff anytime without expiry concerns.  
✅ **Repairs & Technical Services:** Added to domain list.  
✅ **Domain model:** Separate `Domain` model allows flexible domain assignment.

---

## 🧭 API Reference (endpoints & payloads)

Base API mount: `/api/`

### Auth (logaccess)

- POST `/api/auth/register-owner/` ✅
  - Purpose: create a new tenant + owner account (multi-domain).
  - Body (JSON):
    - `business_name` (string)
    - `domain_codes` (list of domain codes, e.g., `["pharmacy", "retail"]`)
    - `email`, `password`
    - optional `first_name`, `last_name`
  - Response: `message`, `user` object, `access_token`, `refresh_token`

- POST `/api/auth/register-staff/` ✅
  - Purpose: register staff using an invite token.
  - Body: `invite_token` (UUID), `email`, `password`, optional `first_name`, `last_name`.

- POST `/api/auth/login/` ✅
  - Body: `email`, `password`.
  - Response: `message`, `user`, `access_token`, `refresh_token`.

- GET `/api/auth/me/` ✅ (auth required)
  - Returns user profile including `tenant` and `role`.

- POST `/api/token/refresh/` ✅
  - Body: `refresh` (refresh token). Response: new access token.

### Staff Invites (logaccess)

- GET `/api/invites/` — list invites (Manager+ only).
- POST `/api/invites/` — create invite (Manager+ only)
  - Body: `email`, `role_type` (cannot invite OWNER via API)
  - **No expiry time limit** — owner manages staff anytime via delete
- GET `/api/invites/{id}/` — retrieve invite.
- DELETE `/api/invites/{id}/` — remove staff (Owner only). **Use this anytime to revoke access.**
- PUT/PATCH: disabled (invites are immutable once created).

### Inventory / Products (inventory)

All routes are tenant-scoped and available under `/api/inventory/products/`.

- GET `/api/inventory/products/` — list products (all staff can read).
- POST `/api/inventory/products/` — create product (Manager+ only).
  - Body: fields depend on tenant domain. Base fields (always present):
    - `name`, `description`, `price`, `cost_price`, `sku`, `image`, `is_active`.
  - Domain-specific fields exist (e.g., `brand`, `category`, `warranty_months`, `room_type`, `is_prescription_required`, etc.).
- GET `/api/inventory/products/{id}/` — retrieve product.
- PUT/PATCH `/api/inventory/products/{id}/` — update (Manager+ only).
- DELETE `/api/inventory/products/{id}/` — delete (Owner only).

Tip: `inventory` uses a dynamic serializer factory — check `inventory/serializers.py` for domain-specific fields.

### Sales / Orders (sales)

All routes are tenant-scoped and available under `/api/sales/orders/`.

- GET `/api/sales/orders/` — list orders.
- POST `/api/sales/orders/` — create order (Manager+ only).
  - Body (example):

```json
{
  "customer_name": "Jane Doe",
  "customer_email": "jane@example.com",
  "customer_phone": "+1234567890",
  "notes": "Deliver after 5pm",
  "discount": 0,
  "line_items": [
    {"product": 1, "quantity": 2},
    {"product": 2, "quantity": 1}
  ]
}
```

- GET `/api/sales/orders/{id}/` — retrieve order.
- PUT/PATCH `/api/sales/orders/{id}/` — update (Manager+ only).
- DELETE `/api/sales/orders/{id}/` — delete (Owner only).

---

## ✅ Notes & developer tips

- Tenancy is enforced by `TenantScopedPermission` (see `logaccess/views.py`). When testing, ensure your test users have `tenant` set.
- Products & serializers are resolved per-tenant domain via `get_serializer_for_domain` in `inventory/serializers.py`.
- Role-based gates are implemented throughout the viewsets (look for `has_tenant_permission` & `is_owner`).

---

## 🔭 Next steps / TODO ideas

- Add `examples/` with curl / Postman collections.
- Add `requirements.txt` exporting the environment.
- Provide API docs (Swagger / Redoc) via `drf-spectacular` or `drf-yasg`.

---

If you'd like, I can also add a simple Postman collection and example curl commands for the main flows (registration, login, create product, create order). 🔧
