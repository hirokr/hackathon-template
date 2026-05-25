"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { useEffect } from "react";
import { getUserPreference, saveUserPreference } from "@/lib/UserPreference";

export function ThemeToggle() {
	const { setTheme, theme } = useTheme();

	useEffect(() => {
		const setUserTheme = async () => {
			const data = await getUserPreference();
			if (data?.theme) setTheme(data.theme);
		};
		setUserTheme();
	}, [setTheme, theme]);

	const ChangeTheme = () => {
		if (theme === "light") {
			setTheme("dark");
			saveUserPreference({ theme: "dark" });
		} else {
			setTheme("light");
			saveUserPreference({ theme: "light" });
		}
	};

	return (
		<Button
			variant='outline'
			size='icon'
			onClick={ChangeTheme}
			className='cursor-pointer'
		>
			<Sun className='h-[1.2rem] w-[1.2rem] scale-100 rotate-0 transition-all dark:scale-0 dark:-rotate-90 '/>
			<Moon className='absolute h-[1.2rem] w-[1.2rem] scale-0 rotate-90 transition-all dark:scale-100 dark:rotate-0' />
			<span className='sr-only'>Toggle theme</span>
		</Button>
	);
}
