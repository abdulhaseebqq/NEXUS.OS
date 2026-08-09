# Day 38 — API Response Consistency & Authentication Dependency Cleanup

## Goal

Audit NEXUS.OS API response consistency and remove duplicated
authentication dependency logic from active API modules.

## API Response Audit

Active API endpoints were reviewed for response consistency.

The backend already uses the centralized success_response() helper
for active endpoint responses.

Raw dictionary returns found during the audit belong to serializer
helper functions and do not represent inconsistent endpoint responses.

## Authentication Dependency Cleanup

Duplicate authentication logic was identified in:

- src/api/profile.py
- src/api/session.py

Both modules duplicated logic for:

- Access token decoding
- User lookup
- Active-user validation
- Authentication error handling

The existing centralized dependency in:

src/core/dependencies.py

is now reused instead.

## Result

Profile and session APIs now use the centralized authentication
dependency instead of maintaining duplicate authentication logic.

This improves:

- API consistency
- Maintainability
- Authentication behavior consistency
- Future security updates

## Validation

- isort passed.
- Black passed.
- MyPy passed for 40 source files.
- Full pytest suite passed.
- 46 tests passing.
- 9 third-party warnings remain.

## Files Changed

- src/api/profile.py
- src/api/session.py
