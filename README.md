# QR Menu API

A production-ready QR code menu management system built with Django REST Framework. Restaurant owners create digital menus with time-based scheduling (breakfast, lunch, dinner), generate QR codes, and customers access the menu by scanning—no app installation needed.

## Why This Project?

Traditional paper menus are expensive to reprint and difficult to update. QR code menus solve this by giving restaurants a permanent QR code that always points to their current menu. This project adds a key feature most solutions lack: **time-based menu scheduling**—the same QR code shows different items at different times of day.

## Features

### Authentication
- Phone-based registration with OTP verification (Iranian phone numbers)
- Two login methods: Phone + Password, or Phone + OTP
- Token-based authentication (DRF Token Auth)
- Profile management: change display name, change phone number with OTP verification
- Security: cooldown periods, OTP expiry (3 minutes), max attempt limits (3), enumeration prevention

### Menu Management
- Create menus with automatic QR code generation
- Menu sections with optional time scheduling (e.g., Breakfast 7am–11am)
- Overlapping sections supported—owner controls priority via ordering
- Bulk item creation (up to 50 items per request)
- Menu availability toggles (soft delete without losing data)
- View tracking for basic analytics

### Public Menu Access
- No authentication required for customers
- Time-based filtering: customers see only sections active at their current time
- Always-visible sections (e.g., "Drinks" available all day)
- Overlapping sections all shown, sorted by owner-defined priority

### Analytics
- Total views (all time)
- Today's views
- Views per day (configurable date range: 7, 30, 365 days)
- Peak day identification

## Tech Stack

- **Python 3.14**
- **Django 6.1**
- **Django REST Framework 3.18**
- **PostgreSQL** (via psycopg 3)
- **Redis** for sessions
- **AWS S3** for media storage (via django-storages + boto3)
- **QR code generation** (via qrcode)
- **pytest** for testing

## Architecture

### Service Layer Pattern

Business logic lives in service classes (`apps/accounts/services/`, `apps/menu/services/`), separate from HTTP handling. Views are thin—they parse input, call services, and format responses.

### ServiceResult Pattern

All services return a consistent `ServiceResult` object:

@dataclass
class ServiceResult(Generic[T]):
    success: bool
    message: str
    data: T | None
    code: str | None  # Machine-readable error code


API Endpoints

All endpoints are prefixed with /api/v1/.

Authentication (/api/v1/accounts/)


POST	/api/v1/accounts/register/	Initiate registration (sends OTP)	

POST	/api/v1/accounts/register/verify/	Verify OTP and create account	

POST	/api/v1/accounts/login/password/	Login with phone + password

POST	/api/v1/accounts/login/send_otp/	Request OTP for login	

POST	/api/v1/accounts/login/verify/	Verify OTP and login	

POST	/api/v1/accounts/logout/	Logout	

GET	/api/v1/accounts/profile/	View own profile	

POST	/api/v1/accounts/change/name/	Change display name	

POST	/api/v1/accounts/change/phone/send_otp/	Request OTP for phone change	

POST	/api/v1/accounts/change/phone/verify/	Verify and change phone number	


POST	/api/v1/menu/menus/	Create menu (auto-creates "Main" section + QR code)	

PATCH	/api/v1/menu/menus/{menu_id}/	Update menu	

DELETE	/api/v1/menu/menus/{menu_id}/	Delete menu	

POST	/api/v1/menu/menus/{menu_id}/sections/	Create section

PATCH	/api/v1/menu/sections/{section_id}/	Update section

DELETE	/api/v1/menu/sections/{section_id}/	Delete section

POST	/api/v1/menu/sections/{section_id}/items/	Add items (bulk, up to 50)

PATCH	/api/v1/menu/items/{item_id}/	Update item	

DELETE	/api/v1/menu/items/{item_id}/	Delete item	

GET	/api/v1/menu/menus/{menu_id}/analytics/	View analytics (optional ?days=30)	


GET	/menu/{menu_id}/	View menu with active sections (records view)



    
