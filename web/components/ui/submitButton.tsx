"use client";
import React, { PropsWithChildren } from "react";
import { Button } from "./button";
import { useFormStatus } from "react-dom";
import { cn } from "@/lib/utils";

type SubmitButtonProps = PropsWithChildren<{
	className?: string;
}>;

const SubmitButton = ({ children, className }: SubmitButtonProps) => {
	const { pending } = useFormStatus();

	return (
		<Button
			type='submit'

			aria-disabled={pending}
			className={cn("w-full mt-2", className)}
		>
			{pending ? "Submitting..." : children}
		</Button>
	);
};

export default SubmitButton;
