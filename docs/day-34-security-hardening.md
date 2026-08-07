# Day 34 — Authentication & Security Hardening

## Goal

Strengthen NEXUS.OS authentication input validation and review the
existing backend security controls without breaking existing behavior.

## Password Security

- Centralized password length constants.
- Minimum password length: 8 characters.
- Maximum password length: 128 characters.
- Added password validation to signup.
- Added bounded password input validation to login and password change.
- Reused centralized password limits for password reset.

## Existing Security Controls Verified

- Password hashing uses pwdlib recommended hashing.
- JWT access and refresh tokens are separated.
- JWT tokens include expiration and unique JTI values.
- JWT secret is loaded from environment configuration.
- Authentication endpoints use rate limiting.
- Forgot-password responses protect against unknown-email enumeration.
- Refresh/session revocation controls are present.

## Authentication Rate Limits Verified

- Signup: 3/minute
- Email verification: 10/minute
- Resend verification: 3/minute
- Forgot password: 3/minute
- Reset password: 5/minute
- Login: 5/minute
- Refresh: 10/minute
- Logout: 10/minute

## Route Audit

Legacy signup/login definitions exist in `src/api/user.py`, but that
router is not registered by the application.

The active authentication routes come from `src/api/auth.py`.

No legacy route was removed during Day 34 to avoid unnecessary changes.

## Token Delivery

Verification and password-reset tokens are currently used directly by
the existing automated tests and development authentication workflow.

Removing these tokens from API responses is deferred until an email
delivery system is implemented.

## Validation

- Black formatting/checks passed.
- MyPy type checks passed.
- Full pytest suite verified against `nexus_os_test`.
- 46 tests passed.
- 417 warnings remain, primarily deprecation warnings.

## Future Security Work

- Disable DEBUG in production.
- Move verification/reset token delivery to email.
- Remove development token exposure after email delivery is available.
- Address `datetime.utcnow()` deprecation warnings separately.