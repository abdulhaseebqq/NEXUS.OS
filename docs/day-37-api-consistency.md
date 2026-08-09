# Day 37 — API Consistency & Legacy Cleanup

## Goal

Clean the NEXUS.OS API structure and remove duplicate legacy route code
without changing active application behavior.

## API Audit

The active application routers are:

- Home
- Health
- System
- Authentication
- Profile
- Sessions
- Admin

All active routers are registered under /api/v1.

## Legacy API Cleanup

Removed:

src/api/user.py

This file contained older duplicate implementations for:

- Signup
- Login
- Refresh token
- Logout
- Profile
- Password change
- Profile image
- Session management

The legacy router was not registered by the application and had no
required imports from the active backend.

## Result

Removing the legacy file reduced duplicate API code and made the active
backend structure easier to maintain.

## Validation

- isort passed.
- Black passed.
- MyPy passed for 40 source files.
- Full pytest suite passed.
- 46 tests passing.
- 9 third-party deprecation warnings remain.

## Active API Structure

Authentication:
src/api/auth.py

Profile:
src/api/profile.py

Sessions:
src/api/session.py

Admin:
src/api/admin.py

System:
src/api/system.py

Health:
src/api/health.py

Home:
src/api/home.py
