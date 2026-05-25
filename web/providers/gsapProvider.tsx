"use client";
import { gsap } from "@/lib/gsap";

export default function GSAPProvider() {
	if (typeof window !== "undefined") {
		gsap.defaults({ ease: "power2.out", duration: 0.8 });
	}

	return null;
}
