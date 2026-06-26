import express from 'express';
import logger from './config/logger.ts';
import helmet from 'helmet';
import morgan from 'morgan';
import cors from 'cors';
import cookieParser from 'cookie-parser';

import redis from 'redis';
import session from 'express-session';
import passport from 'passport';

import authRoutes from './routes/auth.route.ts';
import usersRoutes from './routes/user.route.ts';
import { sendApiError, sendApiSuccess } from '#src/utils/api-response.ts';
import {
  getNumberEnv,
  getOptionalEnv,
  getSameSiteEnv,
  isProduction,
} from '#src/utils/env.ts';

const app = express();
app.use(helmet());

const allowedOrigins = [
  'http://localhost:3000',
  'http://localhost:3001',
  'http://localhost:5173',
  getOptionalEnv('FRONTEND_URL'),
].filter((origin): origin is string => Boolean(origin));

app.use(
  cors({
    origin: allowedOrigins,
    credentials: true,
  })
);
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());

// Store sessions in PostgreSQL via Prisma
app.use(
  session({
    secret: getOptionalEnv('SESSION_SECRET', 'dev-session-secret'),
    resave: false,
    saveUninitialized: true,
    // store: new PrismaSessionStore(),
    cookie: {
      secure: isProduction(),
      sameSite: getSameSiteEnv(),
      maxAge: 15 * 24 * 60 * 60 * 1000,
    },
  })
);
app.use(passport.initialize());
app.use(passport.session());

app.use(
  morgan('combined', {
    stream: { write: message => logger.info(message.trim()) },
  })
);

app.get('/', (req, res) => {
  logger.info('Hello from Tryora!');

  res.status(200).send('Hello from Tryora!');
});

const healthPayload = () => ({
  status: 'OK',
  timestamp: new Date().toISOString(),
  uptime: process.uptime(),
});

app.get('/health', (req, res) => {
  sendApiSuccess(res, { data: healthPayload() });
});

app.head('/health', (req, res) => {
  res.status(200).end();
});

app.get('/api', (req, res) => {
  sendApiSuccess(res, { message: 'Tryora API is running!' });
});

app.use('/api/auth', authRoutes);
app.use('/api/user', usersRoutes);

// Redis session store setup (commented out for now)
export const redisClient = redis.createClient({
  username: getOptionalEnv('REDIS_USERNAME', 'default'),
  password: getOptionalEnv('REDIS_PASSWORD'),
  socket: {
    host: getOptionalEnv('REDIS_HOST', 'localhost'),
    port: getNumberEnv('REDIS_PORT', 6379),
    reconnectStrategy: false,
  },
});

app.use((req, res) => {
  sendApiError(res, { status: 404, message: 'Route not found' });
});

export default app;
