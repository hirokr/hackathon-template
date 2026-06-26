import { BACKEND_URL } from "@/constants/constants";
import { createSession } from "@/lib/auth/session";
import { Session } from "@/types/auth";
import { redirect } from "next/navigation";
import { NextRequest } from "next/server";

export async function GET(req: NextRequest) {
	const { searchParams } = new URL(req.url);
	const status = searchParams.get("status");

	if (status !== "success") {
		redirect("/auth/signin?error=google_oauth_failed");
	}

	const accessToken = req.cookies.get("accessToken")?.value;
	const refreshToken = req.cookies.get("refreshToken")?.value;

	if (!accessToken || !refreshToken) {
		redirect("/auth/signin?error=google_oauth_failed");
	}

	const response = await fetch(`${BACKEND_URL}/api/user/me`, {
		headers: {
			authorization: `Bearer ${accessToken}`,
		},
		cache: "no-store",
	});

	const payload = (await response.json().catch(() => null)) as
		| {
				success?: boolean;
				data?: { user?: Session["user"] };
		  }
		| null;

	if (!response.ok || !payload?.data?.user) {
		redirect("/auth/signin?error=google_oauth_failed");
	}

	await createSession({
		user: payload.data.user,
		accessToken,
		refreshToken,
	});

	redirect("/");
}
