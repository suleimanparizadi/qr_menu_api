# QR Menu API

A production-oriented REST API for managing digital restaurant menus, generating QR codes, scheduling menu availability, and tracking customer engagement.

Built with Django and Django REST Framework, the project provides restaurant owners with an API for managing menus and gives customers access to public menus through QR codes.

## Features

- **Authentication:** Phone-number registration, OTP verification, password login, and OTP-based login.
- **OTP Security:** Expiration, attempt limits, cooldowns, and protection against account enumeration.
- **Menu Management:** Create, update, and delete menus, sections, and menu items.
- **Scheduled Menus:** Configure time-based availability for breakfast, lunch, dinner, and other service periods.
- **QR Code Generation:** Generate QR codes that link directly to public menus.
- **Public Menu API:** Access menus without authentication, with time-based filtering and always-visible sections.
- **Analytics:** Track total views, daily views, historical trends, and peak viewing days.
- **Background Tasks:** Use Celery for asynchronous operations and scheduled maintenance tasks.
- **Object Storage:** Store QR images using an S3-compatible storage backend.
- **Caching and Sessions:** Redis integration for session management and caching.
- **API Versioning:** Versioned endpoints under `/api/v1/`.
- **Service Layer:** Keep business logic separate from API views for better maintainability and testing.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend language |
| Django | Web framework |
| Django REST Framework | REST API development |
| PostgreSQL | Relational database |
| Redis | Caching and session storage |
| Celery | Asynchronous and scheduled tasks |
| S3-compatible storage | QR image storage |
| pytest | Automated testing |
| Docker | Containerized development and deployment |

## Architecture

The project uses a service-layer approach to separate business logic from HTTP request handling.

```text
Client
  |
  v
Django REST Framework
  |
  v
API Views
  |
  v
Service Layer
  |
  +------ PostgreSQL
  |
  +------ Redis
  |
  +------ Celery Tasks
             |
             v
        S3-Compatible Storage
```

Views handle requests and responses, while service classes handle application-specific business rules. Celery workers process background tasks independently of the request-response cycle.

## API Endpoints

### Authentication and Accounts

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/accounts/register/` | Register using a phone number |
| POST | `/api/v1/accounts/register/verify/` | Verify registration OTP |
| POST | `/api/v1/accounts/login/password/` | Log in with a password |
| POST | `/api/v1/accounts/login/send_otp/` | Request a login OTP |
| POST | `/api/v1/accounts/login/verify/` | Verify login OTP |
| POST | `/api/v1/accounts/logout/` | Log out |
| GET | `/api/v1/accounts/profile/` | Retrieve the current profile |
| POST | `/api/v1/accounts/change/name/` | Update the profile name |
| POST | `/api/v1/accounts/change/phone/send_otp/` | Request phone-change verification |
| POST | `/api/v1/accounts/change/phone/verify/` | Verify and update the phone number |

### Menu Management

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/menu/menus/` | Create a menu |
| PATCH | `/api/v1/menu/menus/{menu_id}/` | Update a menu |
| DELETE | `/api/v1/menu/menus/{menu_id}/` | Delete a menu |
| POST | `/api/v1/menu/menus/{menu_id}/sections/` | Create a section |
| PATCH | `/api/v1/menu/sections/{section_id}/` | Update a section |
| DELETE | `/api/v1/menu/sections/{section_id}/` | Delete a section |
| POST | `/api/v1/menu/sections/{section_id}/items/` | Create menu items |
| PATCH | `/api/v1/menu/items/{item_id}/` | Update a menu item |
| DELETE | `/api/v1/menu/items/{item_id}/` | Delete a menu item |
| GET | `/api/v1/menu/menus/{menu_id}/analytics/` | Retrieve menu analytics |
| GET | `/menu/{menu_id}/` | Retrieve a public menu |

**Note:** Authentication requirements and request/response schemas should be documented alongside the API specification.

## Getting Started

### Prerequisites

- Python 3.14
- PostgreSQL
- Redis
- An S3-compatible storage account (for remote QR image storage)
- A message broker accessible to Celery

### 1. Clone the repository

```bash
git clone https://github.com/suleimanparizadi/qr_menu_api.git
cd qr_menu_api
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows, activate it with:

```powershell
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure your local environment.

```dotenv
SECRET_KEY=your-django-secret-key
DEBUG=True

DATABASE_URL=your-database-configuration
REDIS_URL=redis://localhost:6379/0

AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_ENDPOINT_URL=https://your-s3-endpoint

QR_MENU_BASE_URL=http://localhost:8000
```

Adjust these variable names and database settings to match your actual Django configuration. Never commit real credentials or secret keys.

### 5. Run database migrations

```bash
python manage.py migrate
```

### 6. Start the development server

```bash
python manage.py runserver
```

### 7. Start the Celery worker

In a separate terminal:

```bash
celery -A config worker --loglevel=info
```

If your project uses a separate Celery application path, use the corresponding configured application.

### 8. Start Celery Beat (if periodic tasks are configured)

```bash
celery -A config beat --loglevel=info
```

Run the worker and Beat as separate processes. Avoid starting multiple Beat schedulers for the same schedule unless you have coordinated them.

## Testing

Run the automated test suite with:

```bash
pytest
```

If the project uses Django's test runner instead:

```bash
python manage.py test
```

Tests should cover authentication, permissions, OTP expiration and attempt limits, menu scheduling, analytics, storage failures, and background-task behavior.

## Background Tasks

Celery is used to move suitable work outside the HTTP request-response cycle.

Examples include:

- Generating QR images asynchronously.
- Cleaning up expired OTP records.
- Removing QR images associated with deleted menus.
- Running scheduled maintenance jobs.

Tasks that depend on committed database changes should be queued using Django's `transaction.on_commit()`.

## Security Considerations

- Keep secrets and credentials in environment variables.
- Enforce ownership and authorization checks for menu-management endpoints.
- Apply OTP expiration, cooldowns, and attempt limits.
- Validate uploaded files and external storage configuration.
- Avoid exposing sensitive authentication details in API responses or logs.
- Use HTTPS and production-safe Django settings in deployment.

## Future Improvements

- Automated CI pipeline and deployment workflow.
- More comprehensive integration and failure-recovery tests.
- Improved observability, structured logging, and health checks.
- Analytics optimization for larger traffic volumes.
- API documentation using OpenAPI/Swagger.
- More robust retry and monitoring policies for background tasks.

## License

Choose and add a license before distributing or accepting contributions to this project.

---

**Author:** [suleimanparizadi](https://github.com/suleimanparizadi)

**Repository:** [qr_menu_api](https://github.com/suleimanparizadi/qr_menu_api)
