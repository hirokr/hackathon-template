import 'dotenv/config';
import { defineConfig } from 'prisma/config';

// @ts-ignore
// const node_env = process.env.NODE_ENV || 'development';

export default defineConfig({
  schema: 'prisma/schema.prisma',
  migrations: {
    path: 'prisma/migrations',
    seed: 'prisma/seed.ts',
  },
  datasource: {
    // @ts-ignore
    url: process.env['DATABASE_URL'],
  },
});
