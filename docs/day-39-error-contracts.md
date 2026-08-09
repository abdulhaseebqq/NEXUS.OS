# Day 39 — Error Contract Hardening

## Goal

Improve NEXUS.OS API error responses by replacing generic HTTP error
codes with stable status-specific error codes for frontend integration.

## Error Contract

Existing error response shape:

- success
- message
- error.code
- error.details

The response structure was preserved.

## HTTP Error Codes

The following status-based error codes were added:

- 400 -> BAD_REQUEST
- 401 -> UNAUTHORIZED
- 403 -> FORBIDDEN
- 404 -> NOT_FOUND
- 405 -> METHOD_NOT_ALLOWED
- 409 -> CONFLICT
- 413 -> PAYLOAD_TOO_LARGE
- 415 -> UNSUPPORTED_MEDIA_TYPE

Other HTTP exceptions continue to use:

HTTP_ERROR

## Why This Matters

Frontend applications can now react to stable machine-readable error
codes instead of parsing human-readable message text.

## Tests Updated

Existing API tests were updated to validate the new error contract for:

- Unauthorized admin access
- Duplicate signup
- Unauthorized profile access
- Unauthorized session access

## Validation

- isort passed.
- Black passed.
- Flake8 passed.
- MyPy passed for 40 source files.
- Full pytest suite passed.
- 46 tests passing.
- 9 third-party warnings remain.

## Files Changed

- src/backend/server.py
- tests/test_admin.py
- tests/test_auth.py
- tests/test_profile.py
- tests/test_session.py
