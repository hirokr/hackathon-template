import { getSession } from "@/lib/auth/session";
import { signOut } from "@/lib/auth/auth";
import Link from "next/link";
import React from "react";

const SignInButton = async () => {
	const session = await getSession();
	return (
		<div className='flex items-center gap-2 ml-auto'>
			{!session || !session.user ? (
				<>
					<Link href={"/auth/signin"}>Sign In</Link>
					<Link href={"/auth/signup"}>Sign Up</Link>
				</>
			) : (
				<>
					<p>{session.user.name}</p>
					<form action={signOut}>
						<button type='submit'>Sign Out</button>
					</form>
				</>
			)}
		</div>
	);
};

export default SignInButton;
