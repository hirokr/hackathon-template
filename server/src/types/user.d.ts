export type Role = 'USER' | 'ADMIN';

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
  role: Role;
  avatar?: string;
  avatarUrl?: string;
  userBodyImageUrl?: string;
  age?: number;
  gender?: string;
  location?: string;
  interests?: string[];
  emailVerified: boolean;
  isActive: boolean;
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
  verificationToken?: string | null;
  passwordResetTokenHash?: string | null;
  passwordResetExpiresAt?: Date | null;
  isActive?: boolean;
  deletedAt?: Date | null;
};
