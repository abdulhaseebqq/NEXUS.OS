# Day 33 — CI Hardening & Main Branch Protection

## Goal

Harden the NEXUS.OS GitHub workflow and establish a professional
feature-branch ? Pull Request ? CI ? merge workflow.

## Branch Protection

Main branch:
- Restrict deletions
- Block force pushes
- Require Pull Request before merging
- Required approvals: 0
- Require ackend-tests status check

## CI

Required GitHub Actions check:

ackend-tests

Day 32 CI was already verified successfully before starting Day 33.

## Git Workflow

Feature branch:

eature/day-33-ci-hardening

Workflow:

eature branch ? Pull Request ? CI ? main

## GitHub Free Limitation

The repository is private and uses GitHub Free. The created ruleset is
saved, but GitHub indicates that rulesets are not enforced on this
private repository under the current plan.

## Validation

The feature branch was created and pushed successfully.
