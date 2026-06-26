# Auth RBAC Template Fix And Performance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the hackathon template build reliably, support email and Google authentication safely, add real role-based access control to the active Node backend, and improve runtime/dev speed.

**Architecture:** Treat `web` + `server` as the primary stack because the Next frontend points to the Node API. Keep FastAPI as optional/reference unless the product explicitly switches to it. Use httpOnly cookies for browser sessions, server-side Next actions for auth form submissions, Prisma-backed refresh sessions, and explicit middleware for authentication and role authorization.

**Tech Stack:** Next.js 16, React 19, Express 5, Prisma 7, PostgreSQL, Redis, Passport Google OAuth, jose JWT, Zod, Jest/Supertest, Bun or npm-compatible scripts.

---

## File Structure

Create:
- `web/lib/utils.ts` - shared `cn()` utility used by shadcn-style components.
- `web/lib/api-response.ts` - standard Next route response helpers.
- `web/lib/auth/session.ts` - Next-side httpOnly `session` cookie read/write helpers.
- `web/lib/auth/auth.ts` - server actions for signup/signin/signout and backend token refresh.
- `web/lib/gsap.ts` - client-safe GSAP export.
- `web/lib/UserPreference.ts` - theme preference persistence used by toggle component.
- `server/src/middlewares/authorize.middleware.ts` - RBAC middleware.
- `server/src/utils/auth/public-user.ts` - single public-user DTO mapper.
- `server/src/utils/env.ts` - required env parsing for server startup.
- `server/prisma/migrations/<timestamp>_add_roles_and_reset_token_expiry/migration.sql` - role and password reset schema changes.

Modify:
- `server/prisma/schema.prisma` - add `Role`, `role`, password reset fields, indexes.
- `server/src/types/user.d.ts` - include `role`, remove duplicate `age`.
- `server/src/types/authRequest.d.ts` - include `role`.
- `server/src/services/user.service.ts` - select/update role and reset fields.
- `server/src/controllers/auth.controller.ts` - remove token-in-query OAuth redirect, use public DTO, enforce active user state.
- `server/src/controllers/user.controller.ts` - use password reset expiry and clear one-time tokens.
- `server/src/middlewares/authenticate.middleware.ts` - accept bearer or cookie access token and load user role/status.
- `server/src/routes/auth.route.ts` - align auth methods and add current-session endpoint if needed.
- `server/src/routes/user.route.ts` - add example/admin route protected by role.
- `server/src/app.ts` - env-driven CORS/session config, `GET /health`, optional Redis startup safety.
- `server/src/config/google.config.ts` - correct callback path.
- `server/tests/auth.test.ts` - update `/api/auth/*` paths and add security/RBAC cases.
- `web/proxy.ts` - align protected-route check with the Next `session` cookie.
- `web/app/api/auth/google/callback/route.ts` - accept code/status only or rely on backend cookies; no raw tokens in URL.
- `web/types/auth.d.ts` - include role in session user.
- `web/README.md`, `server/README.MD`, `README.MD` - document setup, env, and template scope.
- `server/package.json`, `web/package.json` - add fast check scripts.

---

## Phase 0: Baseline And Dependency Recovery

### Task 1: Install Dependencies And Capture Current Failures

**Files:**
- Modify after this task only if package manager lockfiles need regeneration: `server/bun.lock`, `web/bun.lock`

- [ ] **Step 1: Install server dependencies**

Run:

```bash
cd server
bun install
```

Expected: `node_modules` exists under `server/`.

- [ ] **Step 2: Install web dependencies**

Run:

```bash
cd web
bun install
```

Expected: `node_modules` exists under `web/`.

- [ ] **Step 3: Run server typecheck/build and record failures**

Run:

```bash
cd server
bun run build
```

Expected before fixes: failures related to route/test mismatch or TypeScript issues are allowed. Save exact errors in the task notes.

- [ ] **Step 4: Run web build and record failures**

Run:

```bash
cd web
bun run build
```

Expected before fixes: failures for missing `@/lib/*` modules.

- [ ] **Step 5: Commit dependency baseline if lockfiles changed**

```bash
git add server/bun.lock web/bun.lock
git commit -m "chore: install template dependencies"
```

---

## Phase 1: Make The Frontend Build

### Task 2: Restore Missing Web Lib Modules

**Files:**
- Create: `web/lib/utils.ts`
- Create: `web/lib/api-response.ts`
- Create: `web/lib/auth/session.ts`
- Create: `web/lib/auth/auth.ts`
- Create: `web/lib/gsap.ts`
- Create: `web/lib/UserPreference.ts`
- Modify: `web/types/auth.d.ts`

- [ ] **Step 1: Create `web/lib/utils.ts`**

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
	return twMerge(clsx(inputs));
}
```

- [ ] **Step 2: Create `web/lib/api-response.ts`**

```ts
import { NextResponse } from "next/server";

type SuccessOptions<T> = {
	status?: number;
	message?: string;
	data?: T;
};

type ErrorOptions = {
	status?: number;
	message: string;
	errors?: unknown;
};

export function sendApiSuccess<T>({
	status = 200,
	message,
	data,
}: SuccessOptions<T> = {}) {
	return NextResponse.json(
		{
			success: true,
			...(message ? { message } : {}),
			...(data !== undefined ? { data } : {}),
		},
		{ status },
	);
}

export function sendApiError({
	status = 500,
	message,
	errors,
}: ErrorOptions) {
	return NextResponse.json(
		{
			success: false,
			message,
			...(errors !== undefined ? { errors } : {}),
		},
		{ status },
	);
}
```

- [ ] **Step 3: Update `web/types/auth.d.ts`**

Use this exact session shape:

```ts
export type Role = "USER" | "ADMIN";

export type Session = {
	user: {
		id: string;
		name: string;
		email: string;
		role: Role;
		avatarUrl?: string | null;
		emailVerified?: boolean;
		isActive: boolean;
		userBodyImageUrl?: string | null;
		age?: number | null;
		gender?: string | null;
		location?: string | null;
		interests?: string[] | null;
	};
	accessToken: string;
	refreshToken: string;
};

export type FormState =
	| {
			error?: {
				name?: string[];
				email?: string[];
				password?: string[];
			};
			message?: string;
	  }
	| undefined;
```

- [ ] **Step 4: Create `web/lib/auth/session.ts`**

```ts
import "server-only";

import { cookies } from "next/headers";
import { Session } from "@/types/auth";

const SESSION_COOKIE = "session";
const FIFTEEN_DAYS_SECONDS = 15 * 24 * 60 * 60;

function encodeSession(session: Session) {
	return Buffer.from(JSON.stringify(session), "utf8").toString("base64url");
}

function decodeSession(value: string): Session | null {
	try {
		return JSON.parse(Buffer.from(value, "base64url").toString("utf8")) as Session;
	} catch {
		return null;
	}
}

export async function createSession(session: Session) {
	const cookieStore = await cookies();
	cookieStore.set(SESSION_COOKIE, encodeSession(session), {
		httpOnly: true,
		secure: process.env.NODE_ENV === "production",
		sameSite: "lax",
		path: "/",
		maxAge: FIFTEEN_DAYS_SECONDS,
	});
}

export async function getSession(): Promise<Session | null> {
	const cookieStore = await cookies();
	const value = cookieStore.get(SESSION_COOKIE)?.value;
	return value ? decodeSession(value) : null;
}

export async function updateTokens(tokens: {
	accessToken: string;
	refreshToken: string;
}) {
	const session = await getSession();
	if (!session) return;
	await createSession({ ...session, ...tokens });
}

export async function deleteSession() {
	const cookieStore = await cookies();
	cookieStore.delete(SESSION_COOKIE);
}
```

- [ ] **Step 5: Create `web/lib/auth/auth.ts`**

```ts
"use server";

import { redirect } from "next/navigation";
import { z } from "zod";

import { BACKEND_URL } from "@/constants/constants";
import { FormState, Session } from "@/types/auth";
import { createSession, deleteSession, getSession } from "./session";

type ApiEnvelope<T> = {
	success: boolean;
	message?: string;
	data?: T;
	errors?: Record<string, string[]>;
};

type AuthPayload = {
	user: Session["user"];
	accessToken: string;
	refreshToken: string;
};

const passwordSchema = z
	.string()
	.min(8, "Be at least 8 characters long")
	.regex(/[a-zA-Z]/, "Contain at least one letter.")
	.regex(/[0-9]/, "Contain at least one number.")
	.regex(/[^a-zA-Z0-9]/, "Contain at least one special character.");

const signInSchema = z.object({
	email: z.string().email("Please enter a valid email.").trim(),
	password: passwordSchema,
	redirectTo: z.string().optional(),
});

const signUpSchema = z.object({
	name: z.string().min(2, "Name must be at least 2 characters long.").trim(),
	email: z.string().email("Please enter a valid email.").trim(),
	password: passwordSchema,
});

async function postAuth(path: string, body: unknown) {
	const response = await fetch(`${BACKEND_URL}${path}`, {
		method: "POST",
		headers: { "content-type": "application/json" },
		body: JSON.stringify(body),
		cache: "no-store",
	});

	const payload = (await response.json().catch(() => null)) as
		| ApiEnvelope<AuthPayload>
		| null;

	if (!response.ok || !payload?.success || !payload.data) {
		return {
			error: payload?.errors,
			message: payload?.message ?? "Authentication failed",
		};
	}

	await createSession(payload.data);
	return { redirectTo: "/" };
}

export async function signIn(_state: FormState, formData: FormData) {
	const parsed = signInSchema.safeParse({
		email: formData.get("email"),
		password: formData.get("password"),
		redirectTo: formData.get("redirectTo") || "/",
	});

	if (!parsed.success) {
		return {
			error: parsed.error.flatten().fieldErrors,
			message: "Invalid sign in details",
		};
	}

	const result = await postAuth("/api/auth/signin", {
		email: parsed.data.email,
		password: parsed.data.password,
	});

	if ("message" in result) return result;
	redirect(parsed.data.redirectTo || "/");
}

export async function signUp(_state: FormState, formData: FormData) {
	const parsed = signUpSchema.safeParse({
		name: formData.get("name"),
		email: formData.get("email"),
		password: formData.get("password"),
	});

	if (!parsed.success) {
		return {
			error: parsed.error.flatten().fieldErrors,
			message: "Invalid signup details",
		};
	}

	const result = await postAuth("/api/auth/signup", parsed.data);
	if ("message" in result) return result;
	redirect("/");
}

export async function refreshToken(refreshTokenValue: string) {
	const response = await fetch(`${BACKEND_URL}/api/auth/refresh`, {
		method: "GET",
		headers: {
			cookie: `refreshToken=${refreshTokenValue}`,
		},
		cache: "no-store",
	});

	const payload = (await response.json().catch(() => null)) as
		| ApiEnvelope<{ accessToken: string; refreshToken: string }>
		| null;

	if (!response.ok || !payload?.success || !payload.data) {
		return null;
	}

	return payload.data;
}

export async function signOut() {
	const session = await getSession();

	if (session?.accessToken) {
		await fetch(`${BACKEND_URL}/api/auth/signout`, {
			method: "GET",
			headers: { authorization: `Bearer ${session.accessToken}` },
			cache: "no-store",
		}).catch(() => null);
	}

	await deleteSession();
	redirect("/");
}
```

- [ ] **Step 6: Create `web/lib/gsap.ts`**

```ts
"use client";

import gsap from "gsap";

export { gsap };
```

- [ ] **Step 7: Create `web/lib/UserPreference.ts`**

```ts
"use client";

import { UserPreference } from "@/types/user";

const USER_PREFERENCE_KEY = "template:user-preference";

export function getUserPreference(): UserPreference {
	if (typeof window === "undefined") {
		return { theme: "dark" };
	}

	const raw = window.localStorage.getItem(USER_PREFERENCE_KEY);
	if (!raw) {
		return { theme: "dark" };
	}

	try {
		return JSON.parse(raw) as UserPreference;
	} catch {
		return { theme: "dark" };
	}
}

export function saveUserPreference(preference: UserPreference) {
	if (typeof window === "undefined") return;
	window.localStorage.setItem(USER_PREFERENCE_KEY, JSON.stringify(preference));
}
```

- [ ] **Step 8: Run web build**

Run:

```bash
cd web
bun run build
```

Expected: no missing `@/lib/*` module errors.

- [ ] **Step 9: Commit**

```bash
git add web/lib web/types/auth.d.ts
git commit -m "fix(web): restore auth and utility modules"
```

---

## Phase 2: Align Active Auth Routes And Session Contract

### Task 3: Fix Backend Route Paths And Health Endpoint

**Files:**
- Modify: `server/src/app.ts`
- Modify: `server/src/config/google.config.ts`
- Modify: `server/tests/auth.test.ts`

- [ ] **Step 1: Change Google callback fallback**

In `server/src/config/google.config.ts`, replace:

```ts
'http://localhost:8000/auth/google/callback';
```

with:

```ts
'http://localhost:8000/api/auth/google/callback';
```

- [ ] **Step 2: Add `GET /health` and keep `HEAD /health`**

In `server/src/app.ts`, replace the current `app.head('/health', ...)` block with:

```ts
const healthPayload = () => ({
	status: 'OK',
	timestamp: new Date().toISOString(),
	uptime: process.uptime(),
});

app.get('/health', (req, res) => {
	sendApiSuccess(res, { data: healthPayload() });
});

app.head('/health', (req, res) => {
	res.status(200).end();
});
```

- [ ] **Step 3: Update tests from `/auth/*` to `/api/auth/*`**

In `server/tests/auth.test.ts`, replace these paths:

```ts
.post('/auth/signup')
.post('/auth/signin')
.get('/auth/refresh')
.get('/auth/signout')
```

with:

```ts
.post('/api/auth/signup')
.post('/api/auth/signin')
.get('/api/auth/refresh')
.get('/api/auth/signout')
```

- [ ] **Step 4: Run focused tests**

Run:

```bash
cd server
bun test -- --runInBand server/tests/auth.test.ts
```

Expected: tests run against `/api/auth/*`.

- [ ] **Step 5: Commit**

```bash
git add server/src/app.ts server/src/config/google.config.ts server/tests/auth.test.ts
git commit -m "fix(server): align auth routes and health endpoint"
```

---

### Task 4: Make Backend Auth Accept Bearer Or Cookie Tokens

**Files:**
- Modify: `server/src/middlewares/authenticate.middleware.ts`
- Modify: `server/src/types/authRequest.d.ts`

- [ ] **Step 1: Update `AuthRequest`**

Use:

```ts
import { Request, Response } from 'express';

export interface AuthRequest extends Request {
  userId?: string;
  sessionId?: string;
  role?: 'USER' | 'ADMIN';
}

export type ApiResponse = Response;
```

- [ ] **Step 2: Add token extraction helper**

At the top of `server/src/middlewares/authenticate.middleware.ts`, after imports, add:

```ts
const getAccessTokenFromRequest = (req: AuthRequest) => {
  const authHeader = req.headers.authorization;

  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.split(' ')[1];
  }

  return req.cookies?.accessToken;
};
```

- [ ] **Step 3: Use helper in `authMiddleware`**

Replace:

```ts
const authHeader = req.headers.authorization;

if (!authHeader || !authHeader.startsWith('Bearer ')) {
  return sendApiError(res, { status: 401, message: 'Unauthorized' });
}

const token = authHeader.split(' ')[1];
```

with:

```ts
const token = getAccessTokenFromRequest(req);

if (!token) {
  return sendApiError(res, { status: 401, message: 'Unauthorized' });
}
```

- [ ] **Step 4: Add auth middleware tests**

In `server/tests/auth.test.ts`, add this case under signout tests:

```ts
it('accepts access token from cookie for protected routes', async () => {
  mockVerifyAccessToken.mockResolvedValue({
    userId: 'user-1',
    sessionId: 'session-1',
  });
  mockIsValidSession.mockResolvedValue(true);
  mockDeleteCurrentRefreshToken.mockResolvedValue(undefined);
  mockRevokeSession.mockResolvedValue(undefined);
  mockInvalidateCache.mockResolvedValue(undefined);
  mockClearTokens.mockResolvedValue(undefined);

  const response = await request(app)
    .get('/api/auth/signout')
    .set('Cookie', 'accessToken=access-1');

  expect(response.status).toBe(200);
});
```

- [ ] **Step 5: Run tests**

```bash
cd server
bun test -- --runInBand server/tests/auth.test.ts
```

Expected: new cookie auth test passes.

- [ ] **Step 6: Commit**

```bash
git add server/src/middlewares/authenticate.middleware.ts server/src/types/authRequest.d.ts server/tests/auth.test.ts
git commit -m "fix(server): accept cookie access token for auth middleware"
```

---

## Phase 3: Remove OAuth Token Leakage

### Task 5: Stop Sending Tokens In Google Redirect URLs

**Files:**
- Modify: `server/src/controllers/auth.controller.ts`
- Modify: `web/app/api/auth/google/callback/route.ts`

- [ ] **Step 1: Replace OAuth redirect query construction**

In `server/src/controllers/auth.controller.ts`, replace both redirect blocks that include `accessToken=${accessToken}&refreshToken=${refreshToken}` with:

```ts
await saveToCookie(res, refreshToken, accessToken);

const query = new URLSearchParams({
  status: 'success',
}).toString();

return res.redirect(`${frontend}/api/auth/google/callback?${query}`);
```

Keep `saveRefreshToken(...)` and `setCache(...)` before the redirect.

- [ ] **Step 2: Replace frontend Google callback route**

Replace `web/app/api/auth/google/callback/route.ts` with:

```ts
import { redirect } from "next/navigation";
import { NextRequest } from "next/server";

export async function GET(req: NextRequest) {
	const { searchParams } = new URL(req.url);
	const status = searchParams.get("status");

	if (status !== "success") {
		redirect("/auth/signin?error=google_oauth_failed");
	}

	redirect("/");
}
```

- [ ] **Step 3: Add a regression test for redirect safety**

In `server/tests/auth.test.ts`, add a helper-level or route-level test if Google callback is mocked. The assertion must check:

```ts
expect(response.headers.location).not.toContain('accessToken=');
expect(response.headers.location).not.toContain('refreshToken=');
```

If the current Passport test setup cannot call the callback safely, add this check after Google callback mocking is stabilized in Task 6.

- [ ] **Step 4: Run builds**

```bash
cd server && bun run build
cd ../web && bun run build
```

Expected: both builds pass.

- [ ] **Step 5: Commit**

```bash
git add server/src/controllers/auth.controller.ts web/app/api/auth/google/callback/route.ts server/tests/auth.test.ts
git commit -m "fix(auth): stop leaking oauth tokens in redirect urls"
```

---

## Phase 4: Add Real RBAC To The Node Backend

### Task 6: Add Prisma Role Schema

**Files:**
- Modify: `server/prisma/schema.prisma`
- Create: `server/prisma/migrations/<timestamp>_add_roles_and_reset_token_expiry/migration.sql`

- [ ] **Step 1: Add `Role` enum to Prisma**

In `server/prisma/schema.prisma`, after `Gender`, add:

```prisma
enum Role {
  USER
  ADMIN
}
```

- [ ] **Step 2: Add role and reset fields to `User`**

Inside `model User`, add:

```prisma
  role                   Role      @default(USER)
  passwordResetTokenHash String?   @map("password_reset_token_hash") @db.VarChar(255)
  passwordResetExpiresAt DateTime? @map("password_reset_expires_at")
```

Add indexes:

```prisma
  @@index([role])
  @@index([passwordResetTokenHash])
```

- [ ] **Step 3: Add refresh-token performance index**

Inside `model RefreshToken`, add:

```prisma
  @@index([userId, sessionId, isActive, expiresAt])
```

- [ ] **Step 4: Create migration**

Run:

```bash
cd server
bunx prisma migrate dev --name add_roles_and_reset_token_expiry
```

Expected: migration SQL is generated under `server/prisma/migrations`.

- [ ] **Step 5: Regenerate Prisma client**

```bash
cd server
bun run db:gen
```

Expected: generated files include `Role`.

- [ ] **Step 6: Commit**

```bash
git add server/prisma server/src/generated
git commit -m "feat(server): add user roles and reset token expiry"
```

---

### Task 7: Add Public User Mapper And Role-Aware Types

**Files:**
- Create: `server/src/utils/auth/public-user.ts`
- Modify: `server/src/types/user.d.ts`
- Modify: `server/src/services/user.service.ts`

- [ ] **Step 1: Replace `ReturnUserDto`**

In `server/src/types/user.d.ts`, use:

```ts
export type Role = 'USER' | 'ADMIN';

export type CreateUserDto = {
  email: string;
  name: string;
  verificationToken: string;
  passwordHash: string;
};

export type ReturnUserDto = {
  id: string;
  email: string;
  name: string;
  role: Role;
  avatar?: string;
  avatarUrl?: string;
  userBodyImageUrl?: string;
  age?: number;
  gender?: string;
  location?: string;
  interests?: string[];
  emailVerified: boolean;
  isActive: boolean;
};

export type UpdateUserProfileDto = {
  userId: string;
  name?: string;
  avatarUrl?: string;
  userBodyImageUrl?: string;
  age?: number;
  gender?: string;
  location?: string;
  interests?: string[];
  verificationToken?: string | null;
  passwordResetTokenHash?: string | null;
  passwordResetExpiresAt?: Date | null;
  isActive?: boolean;
  deletedAt?: Date | null;
};
```

- [ ] **Step 2: Create public user mapper**

```ts
import { ReturnUserDto } from '#src/types/user.js';

type UserLike = {
  id: string;
  email: string;
  name: string;
  role?: string | null;
  avatarUrl?: string | null;
  userBodyImageUrl?: string | null;
  age?: number | null;
  gender?: string | null;
  location?: string | null;
  interests?: string[] | null;
  emailVerified: boolean;
  isActive: boolean;
};

export function toPublicUser(user: UserLike): ReturnUserDto {
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role === 'ADMIN' ? 'ADMIN' : 'USER',
    avatar: user.avatarUrl || undefined,
    avatarUrl: user.avatarUrl || undefined,
    userBodyImageUrl: user.userBodyImageUrl || undefined,
    age: user.age || undefined,
    gender: user.gender || undefined,
    location: user.location || undefined,
    interests: user.interests || undefined,
    emailVerified: user.emailVerified,
    isActive: user.isActive,
  };
}
```

- [ ] **Step 3: Use mapper in `user.service.ts`**

Import:

```ts
import { toPublicUser } from '#src/utils/auth/public-user.ts';
```

In `findUserById`, add `role: true` to `select`.

In `createUser`, replace manual `newUser` object with:

```ts
return toPublicUser(user);
```

In `updateUserProfile`, replace manual return object with:

```ts
return toPublicUser(user);
```

- [ ] **Step 4: Run server build**

```bash
cd server
bun run build
```

Expected: no duplicate type errors, no missing `role` errors.

- [ ] **Step 5: Commit**

```bash
git add server/src/types/user.d.ts server/src/services/user.service.ts server/src/utils/auth/public-user.ts
git commit -m "feat(server): return role-aware public user dto"
```

---

### Task 8: Add Authorization Middleware

**Files:**
- Create: `server/src/middlewares/authorize.middleware.ts`
- Modify: `server/src/middlewares/authenticate.middleware.ts`
- Modify: `server/src/routes/user.route.ts`
- Modify: `server/tests/auth.test.ts`

- [ ] **Step 1: Create `authorize.middleware.ts`**

```ts
import { NextFunction, Response } from 'express';
import { AuthRequest } from '#src/types/authRequest.js';
import { sendApiError } from '#src/utils/api-response.ts';

type Role = 'USER' | 'ADMIN';

export const requireRole =
  (...roles: Role[]) =>
  (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.role) {
      return sendApiError(res, { status: 401, message: 'Unauthorized' });
    }

    if (!roles.includes(req.role)) {
      return sendApiError(res, { status: 403, message: 'Forbidden' });
    }

    next();
  };
```

- [ ] **Step 2: Load role in auth middleware**

In `server/src/middlewares/authenticate.middleware.ts`, import:

```ts
import { findUserById } from '#src/services/user.service.ts';
```

After session validation succeeds, add:

```ts
const user = await findUserById(userId);
if (!user || !user.isActive) {
  return sendApiError(res, {
    status: 401,
    message: 'User is inactive or deleted',
  });
}
```

Then set:

```ts
(req as AuthRequest).role = user.role;
```

- [ ] **Step 3: Add an admin-only route example**

In `server/src/routes/user.route.ts`, import:

```ts
import { requireRole } from '#src/middlewares/authorize.middleware.ts';
```

After `router.use(authMiddleware);`, add:

```ts
router.get('/admin/check', requireRole('ADMIN'), (req, res) => {
  res.status(200).json({ success: true, data: { allowed: true } });
});
```

- [ ] **Step 4: Add RBAC tests**

In `server/tests/auth.test.ts`, mock `findUserById` separately and add:

```ts
it('returns 403 for non-admin user on admin route', async () => {
  mockVerifyAccessToken.mockResolvedValue({
    userId: 'user-1',
    sessionId: 'session-1',
  });
  mockIsValidSession.mockResolvedValue(true);
  mockFindUserById.mockResolvedValue({
    id: 'user-1',
    role: 'USER',
    isActive: true,
  });

  const response = await request(app)
    .get('/api/user/admin/check')
    .set('Authorization', 'Bearer access-1');

  expect(response.status).toBe(403);
});

it('allows admin user on admin route', async () => {
  mockVerifyAccessToken.mockResolvedValue({
    userId: 'admin-1',
    sessionId: 'session-1',
  });
  mockIsValidSession.mockResolvedValue(true);
  mockFindUserById.mockResolvedValue({
    id: 'admin-1',
    role: 'ADMIN',
    isActive: true,
  });

  const response = await request(app)
    .get('/api/user/admin/check')
    .set('Authorization', 'Bearer access-1');

  expect(response.status).toBe(200);
  expect(response.body.data.allowed).toBe(true);
});
```

- [ ] **Step 5: Run tests**

```bash
cd server
bun test -- --runInBand server/tests/auth.test.ts
```

Expected: RBAC tests pass.

- [ ] **Step 6: Commit**

```bash
git add server/src/middlewares server/src/routes/user.route.ts server/tests/auth.test.ts
git commit -m "feat(server): add role based authorization middleware"
```

---

## Phase 5: Harden Email Auth And Password Reset

### Task 9: Enforce Active And Verified Account Policy

**Files:**
- Modify: `server/src/controllers/auth.controller.ts`
- Modify: `server/tests/auth.test.ts`

- [ ] **Step 1: Block inactive users in signin**

In `signin`, after `if (!user)`, add:

```ts
if (!user.isActive || user.deletedAt) {
  return sendApiError(res, {
    status: 403,
    message: 'Account is inactive',
  });
}
```

- [ ] **Step 2: Decide email verification policy**

For hackathon templates, allow login before verification but expose `emailVerified` to the app. If the product requires verified-only access, use this block instead:

```ts
if (!user.emailVerified) {
  return sendApiError(res, {
    status: 403,
    message: 'Please verify your email before signing in',
  });
}
```

Choose one policy and document it in `server/README.MD`.

- [ ] **Step 3: Add inactive-user test**

```ts
it('blocks inactive users from signing in', async () => {
  mockFindUserByEmail.mockResolvedValue({
    id: 'user-1',
    email: 'test@example.com',
    name: 'John Doe',
    passwordHash: 'hashed-pass',
    emailVerified: true,
    isActive: false,
    deletedAt: null,
  });

  const response = await request(app)
    .post('/api/auth/signin')
    .send({ email: 'test@example.com', password: 'Password1!' });

  expect(response.status).toBe(403);
});
```

- [ ] **Step 4: Run tests and commit**

```bash
cd server
bun test -- --runInBand server/tests/auth.test.ts
git add server/src/controllers/auth.controller.ts server/tests/auth.test.ts server/README.MD
git commit -m "fix(auth): enforce inactive account policy"
```

---

### Task 10: Use Expiring One-Time Password Reset Tokens

**Files:**
- Modify: `server/src/controllers/user.controller.ts`
- Modify: `server/src/services/user.service.ts`
- Modify: `server/tests/auth.test.ts`

- [ ] **Step 1: Hash reset tokens before storage**

In `forgotPassword`, replace:

```ts
await updateUserProfile({ userId: user.id, verificationToken: resetToken });
```

with:

```ts
const resetTokenHash = hashTokenCrypto(resetToken);
await updateUserProfile({
  userId: user.id,
  passwordResetTokenHash: resetTokenHash,
  passwordResetExpiresAt: new Date(Date.now() + 60 * 60 * 1000),
});
```

Import `hashTokenCrypto` from `#src/utils/jwt/tokens.ts`.

- [ ] **Step 2: Add service lookup**

In `server/src/services/user.service.ts`, add:

```ts
export async function findUserByPasswordResetTokenHash(tokenHash: string) {
  return prisma.user.findFirst({
    where: {
      passwordResetTokenHash: tokenHash,
      passwordResetExpiresAt: { gt: new Date() },
      deletedAt: null,
      isActive: true,
    },
  });
}
```

- [ ] **Step 3: Update reset password**

In `resetPassword`, replace:

```ts
const user = await findUserByVerificationToken(token);
```

with:

```ts
const tokenHash = hashTokenCrypto(token);
const user = await findUserByPasswordResetTokenHash(tokenHash);
```

After `await updateUserPassword(...)`, add:

```ts
await updateUserProfile({
  userId: user.id,
  passwordResetTokenHash: null,
  passwordResetExpiresAt: null,
});
```

- [ ] **Step 4: Run tests**

```bash
cd server
bun test -- --runInBand server/tests/auth.test.ts
```

Expected: reset tests pass and expired tokens fail.

- [ ] **Step 5: Commit**

```bash
git add server/src/controllers/user.controller.ts server/src/services/user.service.ts server/tests/auth.test.ts
git commit -m "fix(auth): use expiring one time password reset tokens"
```

---

## Phase 6: Runtime Speed And Stability

### Task 11: Make Redis Non-Fatal And Fast On Local Setups

**Files:**
- Modify: `server/src/app.ts`
- Modify: `server/src/server.ts`
- Modify: `server/src/utils/redis.ts`

- [ ] **Step 1: Create Redis only when configured**

In `server/src/app.ts`, replace Redis client creation with:

```ts
export const redisClient = redis.createClient({
  username: process.env.REDIS_USERNAME || 'default',
  password: process.env.REDIS_PASSWORD,
  socket: {
    host: process.env.REDIS_HOST || 'localhost',
    port: Number(process.env.REDIS_PORT || 6379),
    reconnectStrategy: false,
  },
});
```

- [ ] **Step 2: Guard cache reads**

In `server/src/utils/redis.ts`, add:

```ts
const isRedisReady = () => redisClient.isOpen;
```

At the start of `getSetCache`, add:

```ts
if (!isRedisReady()) {
  return cb();
}
```

At the start of `setCache`, `invalidateCache`, `getCache`, and `deleteUserCache`, return early when Redis is not open:

```ts
if (!isRedisReady()) return;
```

For `getCache`, use:

```ts
if (!isRedisReady()) return null;
```

- [ ] **Step 3: Keep server booting when Redis is absent**

In `server/src/server.ts`, keep the existing catch, but make sure no code exits the process on Redis connection failure.

- [ ] **Step 4: Run server without Redis env**

Run:

```bash
cd server
env -u REDIS_HOST -u REDIS_PASSWORD bun run dev
```

Expected: server starts and `/health` returns 200. Redis failure is logged but does not crash the API.

- [ ] **Step 5: Commit**

```bash
git add server/src/app.ts server/src/server.ts server/src/utils/redis.ts
git commit -m "fix(server): make redis cache optional in local development"
```

---

### Task 12: Add Fast Check Scripts

**Files:**
- Modify: `server/package.json`
- Modify: `web/package.json`
- Modify: `README.MD`

- [ ] **Step 1: Add server scripts**

In `server/package.json`, add:

```json
"check": "bun run build && bun test -- --runInBand",
"check:fast": "tsc --noEmit",
"test:auth": "cross-env NODE_OPTIONS=--experimental-vm-modules jest --runInBand server/tests/auth.test.ts"
```

If `build` already runs `tsc`, keep `check:fast` as:

```json
"check:fast": "tsc --noEmit"
```

- [ ] **Step 2: Add web scripts**

In `web/package.json`, add:

```json
"typecheck": "tsc --noEmit",
"check": "bun run typecheck && bun run lint && bun run build",
"check:fast": "bun run typecheck"
```

- [ ] **Step 3: Add top-level README quickstart**

In `README.MD`, replace the single `# Template` content with:

```md
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
```

- [ ] **Step 4: Commit**

```bash
git add server/package.json web/package.json README.MD
git commit -m "chore: add fast project verification scripts"
```

---

### Task 13: Reduce API Hot-Path Database Work

**Files:**
- Modify: `server/src/controllers/auth.controller.ts`
- Modify: `server/src/middlewares/authenticate.middleware.ts`
- Modify: `server/src/services/token.service.ts`

- [ ] **Step 1: Cache session validity as boolean**

In Google callback, replace:

```ts
await setCache(
  makeUserSessionCacheKey(user.id, newSessionId),
  user.id,
  refreshToken
);
```

with:

```ts
await setCache(makeUserSessionCacheKey(user.id, newSessionId), user.id, true);
```

In signin, after `saveRefreshToken(...)`, add:

```ts
await setCache(makeUserSessionCacheKey(user.id, sessionId), user.id, true);
```

- [ ] **Step 2: Select only needed session fields**

In `server/src/services/token.service.ts`, ensure `isValidSession` keeps:

```ts
select: { userId: true, sessionId: true },
```

Do not select full token rows on auth middleware hot path.

- [ ] **Step 3: Run auth tests**

```bash
cd server
bun test -- --runInBand server/tests/auth.test.ts
```

Expected: session validation behavior remains unchanged.

- [ ] **Step 4: Commit**

```bash
git add server/src/controllers/auth.controller.ts server/src/middlewares/authenticate.middleware.ts server/src/services/token.service.ts
git commit -m "perf(auth): cache session validity on login"
```

---

## Phase 7: Template Cleanup

### Task 14: Remove Split-Brain Confusion Between Node And FastAPI

**Files:**
- Modify: `README.MD`
- Modify: `fastapi/README.md`

- [ ] **Step 1: Document primary backend**

Add this to top-level `README.MD`:

```md
## Backend Choice

The active frontend integration uses `server/` (Express + Prisma). The `fastapi/` directory is an optional alternate implementation and should not be edited for the main template unless the project explicitly switches to FastAPI.
```

- [ ] **Step 2: Mark FastAPI as optional**

At the top of `fastapi/README.md`, add:

```md
# Optional FastAPI Backend

This is an alternate backend implementation. The default template runtime uses `server/`.
```

- [ ] **Step 3: Commit**

```bash
git add README.MD fastapi/README.md
git commit -m "docs: clarify primary backend for template"
```

---

## Final Verification

- [ ] **Step 1: Run server full check**

```bash
cd server
bun run check
```

Expected: TypeScript build and Jest tests pass.

- [ ] **Step 2: Run web full check**

```bash
cd web
bun run check
```

Expected: typecheck, lint, and Next build pass.

- [ ] **Step 3: Run local smoke**

Terminal 1:

```bash
cd server
bun run dev
```

Terminal 2:

```bash
cd web
bun run dev
```

Terminal 3:

```bash
curl -i http://localhost:8000/health
curl -i http://localhost:8000/api
```

Expected:
- `/health` returns HTTP 200.
- `/api` returns `{ "success": true, "message": "Tryora API is running!" }`.
- Web app loads at `http://localhost:3000`.
- Sign up creates a user.
- Sign in creates a Next `session` cookie.
- Protected pages redirect unauthenticated users.
- `/api/user/admin/check` returns 403 for `USER`, 200 for `ADMIN`.
- Google OAuth completes without `accessToken=` or `refreshToken=` appearing in the browser URL.

---

## Risk Notes

- The `session` cookie plan stores a base64 JSON session. That restores the current template quickly, but production should sign or encrypt the cookie using `jose` or `iron-session`.
- If cross-site frontend/backend deployment is required, cookie `sameSite` and `secure` settings must be configured per deployment domain.
- If the project keeps both Node and FastAPI backends, schema and auth behavior will drift unless one is documented as primary.
- Redis must be optional for hackathon onboarding speed; the database remains the source of truth for active sessions.

## Suggested Commit Sequence

1. `chore: install template dependencies`
2. `fix(web): restore auth and utility modules`
3. `fix(server): align auth routes and health endpoint`
4. `fix(server): accept cookie access token for auth middleware`
5. `fix(auth): stop leaking oauth tokens in redirect urls`
6. `feat(server): add user roles and reset token expiry`
7. `feat(server): return role-aware public user dto`
8. `feat(server): add role based authorization middleware`
9. `fix(auth): enforce inactive account policy`
10. `fix(auth): use expiring one time password reset tokens`
11. `fix(server): make redis cache optional in local development`
12. `chore: add fast project verification scripts`
13. `perf(auth): cache session validity on login`
14. `docs: clarify primary backend for template`

