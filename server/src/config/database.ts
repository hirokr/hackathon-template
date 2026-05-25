import { DATABASE_URL, NODE_ENV } from '#src/constant.ts';
import { PrismaClient } from '../generated/client.ts';
import { PrismaPg } from '@prisma/adapter-pg';

const connectionString = `${DATABASE_URL}`;

if (!connectionString) {
  if (NODE_ENV === 'development')
    console.warn(
      'WARNING: $DATABASE_URL is not set. Prisma client will still be created but may fail on usage.'
    );
}

const adapter = new PrismaPg({ connectionString });
const prisma = new PrismaClient({ adapter });

export default prisma;
