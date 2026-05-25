import { NextRequest, NextResponse } from "next/server";

const PUBLIC_ROUTES = new Set(["/", "/style-discovery"]);

const isAssetRequest = (pathname: string) => /\.[^/]+$/.test(pathname);

export function proxy(request: NextRequest) {
	const { pathname } = request.nextUrl;

	if (
		pathname.startsWith("/_next") ||
		pathname.startsWith("/api") ||
		pathname.startsWith("/discover") ||
		pathname.startsWith("/products") ||
		pathname.startsWith("/trending") ||
		pathname === "/favicon.ico" ||
		isAssetRequest(pathname)
	) {
		return NextResponse.next();
	}

	const hasSession = Boolean(request.cookies.get("session")?.value);
	const isAuthRoute = pathname.startsWith("/auth");
	const isPublicRoute =
		PUBLIC_ROUTES.has(pathname) || pathname.startsWith("/public-share") || isAuthRoute;

	if (!hasSession && !isPublicRoute) {
		const redirectUrl = request.nextUrl.clone();
		redirectUrl.pathname = "/";
		redirectUrl.search = "";
		return NextResponse.redirect(redirectUrl);
	}

	return NextResponse.next();
}

export const config = {
	matcher: ["/:path*"],
};
