# Full Hackathon Template

Next.js frontend plus Express/Prisma backend with email auth, Google OAuth, httpOnly session cookies, RBAC, profile settings, and optional Redis session caching.

## Quick Start

```bash
cd server
bun install
cp .env.example .env
bun run db:migrate
bun run dev
```

```bash
cd web
bun install
cp .env.example .env
bun run dev
```

## Verification

```bash
cd server && bun run check
cd ../web && bun run check
```

## Backend Choice

The active frontend integration uses `server/` (Express + Prisma). The `fastapi/` directory is an optional alternate implementation and should not be edited for the main template unless the project explicitly switches to FastAPI.

## Required Backend Env

- `DATABASE_URL`
- `JWT_SECRET`
- `REFRESH_JWT_SECRET`
- `FRONTEND_URL`
- `GOOGLE_CLIENT_ID`
- `GOOGLE_CLIENT_SECRET`
- `GOOGLE_CALLBACK_URL`

## Optional Backend Env

- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_USERNAME`
- `REDIS_PASSWORD`
- `COOKIE_SAME_SITE`
- `SESSION_SECRET`
