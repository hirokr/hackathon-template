export type CreateUserDto = {
  email: string;
  name: string;
  verificationToken: string;
  passwordHash: string;
};

export type ReturnUserDto = {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  userBodyImageUrl?: string;
  age?: number;
  gender?: string;
  location?: string;
  interests?: string[];
  emailVerified: boolean;
  isActive: boolean;
  age?: number;
};

export type UpdateUserProfileDto = {
  userId: string;
  name?: string;
  avatarUrl?: string;
  userBodyImageUrl?: string;
  age?: number;
  gender?: string;
  location?: string;
  interests?: string[];
  verificationToken?: string;
  isActive?: boolean;
  deletedAt?: Date | null;
};
