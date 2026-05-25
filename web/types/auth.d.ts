export type Session = {
	user: {
		id: string;
		name: string;
		email: string;
		avatarUrl?: string;
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
