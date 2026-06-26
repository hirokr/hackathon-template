# Next.js Frontend

Frontend for the template. It uses server actions for email auth, the backend Google OAuth callback, and an httpOnly `session` cookie for browser sessions.

## Setup

```bash
bun install
cp .env.example .env
bun run dev
```

## Verification

```bash
bun run check
```

## Required Env

- `SESSION_SECRET_KEY`
- `NEXT_PUBLIC_API_URL` or the project-specific backend URL variable used by `constants/constants.ts`
