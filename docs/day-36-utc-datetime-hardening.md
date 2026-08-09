# Day 36 — UTC Datetime Hardening

## Goal

Modernize NEXUS.OS datetime handling and remove deprecated
datetime.utcnow() usage without changing existing database behavior.

## UTC Strategy

The database currently stores naive UTC timestamps.

A centralized utc_now() helper was added that uses timezone-aware
datetime generation internally and converts it to naive UTC for
compatibility with the existing database schema.

## New Utility

Added:

src/core/datetime_utils.py

The utc_now() helper replaces deprecated datetime.utcnow() usage.

## Updated Areas

- User creation timestamps
- Email verification expiry
- Password reset expiry
- Session last activity
- Session logout timestamps
- Database model defaults
- Authentication expiry checks
- Activity/session timestamps

## Compatibility

No database migration was required.

Existing naive UTC database behavior was preserved.

## Validation

- Black passed.
- MyPy passed for 41 source files.
- Full pytest suite passed.
- 46 tests passing.
- Warning count reduced from 417 to 9.

## Remaining Warnings

The remaining warnings come from third-party libraries such as
FastAPI/Starlette/SlowAPI and are not caused by NEXUS.OS datetime code.
