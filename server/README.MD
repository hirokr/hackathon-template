# Express Backend

Primary API for the template. It provides email auth, Google OAuth, JWT access tokens, Prisma-backed refresh sessions, role-based authorization, profile routes, and optional Redis session caching.

## Setup

```bash
bun install
cp .env.example .env
bun run db:migrate
bun run db:gen
bun run dev
```

## Verification

```bash
bun run check
bun run test:auth
```

## Auth Policy

Inactive or deleted users cannot sign in. Email verification status is exposed to the app, but unverified users are allowed to sign in by default so hackathon teams can decide their own gating policy.

## RBAC

Users have `USER` or `ADMIN` roles. Protected routes use `authMiddleware`; role-gated routes additionally use `requireRole(...)`.

## Redis

Redis is optional for local development. If Redis is not connected, cache helpers fall back to the database-backed session checks.
