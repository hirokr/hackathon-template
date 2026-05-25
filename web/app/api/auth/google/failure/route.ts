import { redirect } from "next/navigation";

export async function GET() {
  redirect("/auth/signin?error=google_oauth_failed");
}
