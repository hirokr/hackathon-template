type SameSite = 'lax' | 'strict' | 'none';

const getEnv = (key: string) => process.env[key];

export const getOptionalEnv = (key: string, fallback?: string) =>
  getEnv(key) || fallback;

export const getRequiredEnv = (key: string) => {
  const value = getEnv(key);
  if (!value) {
    throw new Error(`${key} is required`);
  }

  return value;
};

export const getNumberEnv = (key: string, fallback: number) => {
  const value = getEnv(key);
  if (!value) return fallback;

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
};

export const getSameSiteEnv = (
  key = 'COOKIE_SAME_SITE',
  fallback: SameSite = 'lax'
): SameSite => {
  const value = getEnv(key)?.toLowerCase();
  return value === 'lax' || value === 'strict' || value === 'none'
    ? value
    : fallback;
};

export const isProduction = () => process.env.NODE_ENV === 'production';
