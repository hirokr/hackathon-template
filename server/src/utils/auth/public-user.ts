import { ReturnUserDto } from '#src/types/user.js';

type UserLike = {
  id: string;
  email: string;
  name: string;
  role?: string | null;
  avatarUrl?: string | null;
  userBodyImageUrl?: string | null;
  age?: number | null;
  gender?: string | null;
  location?: string | null;
  interests?: string[] | null;
  emailVerified: boolean;
  isActive: boolean;
};

export function toPublicUser(user: UserLike): ReturnUserDto {
  return {
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role === 'ADMIN' ? 'ADMIN' : 'USER',
    avatar: user.avatarUrl || undefined,
    avatarUrl: user.avatarUrl || undefined,
    userBodyImageUrl: user.userBodyImageUrl || undefined,
    age: user.age || undefined,
    gender: user.gender || undefined,
    location: user.location || undefined,
    interests: user.interests || undefined,
    emailVerified: user.emailVerified,
    isActive: user.isActive,
  };
}
