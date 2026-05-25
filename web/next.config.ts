import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	turbopack: {
		root: __dirname,
	},
	images: {
		remotePatterns: [
			{
				protocol: "https",
				hostname: "**.ufs.sh",
			},
			{
				protocol: "https",
				hostname: "**", // Allows all HTTPS domains
			},
			{
				protocol: "http",
				hostname: "**", // Allows all HTTP domains
			},
		],
	},
};

export default nextConfig;
