import { PropsWithChildren } from "react";
import { AuthPageShell } from "./_components/AuthPageShell";

const AuthLayout = ({ children }: PropsWithChildren) => {
	return <AuthPageShell>{children}</AuthPageShell>;
};

export default AuthLayout;
