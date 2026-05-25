import type { ConnectionOptions } from 'bullmq';

const redisHost = process.env.REDIS_HOST || '127.0.0.1';
const redisPort = Number(process.env.REDIS_PORT || 6379);
const redisDb = process.env.REDIS_DB ? Number(process.env.REDIS_DB) : undefined;

if (Number.isNaN(redisPort)) {
  throw new Error('REDIS_PORT must be a valid number');
}

if (redisDb !== undefined && Number.isNaN(redisDb)) {
  throw new Error('REDIS_DB must be a valid number when provided');
}

export const bullmqConnection: ConnectionOptions = {
  host: redisHost,
  port: redisPort,
  ...(process.env.REDIS_PASSWORD
    ? { password: process.env.REDIS_PASSWORD }
    : {}),
  ...(redisDb !== undefined ? { db: redisDb } : {}),
};
