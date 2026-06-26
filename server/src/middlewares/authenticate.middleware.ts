// middleware/auth.middleware.ts
import { verifyAccessToken } from '#src/utils/jwt/tokens.ts';
import { Response, NextFunction, Request, RequestHandler } from 'express';
import { AuthRequest } from '#src/types/authRequest.js';
import { getSetCache, makeUserSessionCacheKey } from '#src/utils/redis.ts';
import { isValidSession } from '#src/services/token.service.ts';
import { z, ZodError } from 'zod/v3';
import { sendApiError } from '#src/utils/api-response.ts';
import { findUserById } from '#src/services/user.service.ts';

const getAccessTokenFromRequest = (req: AuthRequest) => {
  const authHeader = req.headers.authorization;

  if (authHeader?.startsWith('Bearer ')) {
    return authHeader.split(' ')[1];
  }

  return req.cookies?.accessToken;
};

export const authMiddleware = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const token = getAccessTokenFromRequest(req);

    if (!token) {
      return sendApiError(res, { status: 401, message: 'Unauthorized' });
    }

    const getData = await verifyAccessToken(token);
    const { userId, sessionId } = getData || {};

    if (!userId || !sessionId) {
      return sendApiError(res, {
        status: 401,
        message: 'Invalid token payload',
      });
    }

    const cacheKey = makeUserSessionCacheKey(userId, sessionId);
    const isActiveSession = await getSetCache(cacheKey, () =>
      isValidSession(userId, sessionId)
    );

    if (!isActiveSession) {
      return sendApiError(res, {
        status: 401,
        message: 'Invalid or expired session',
      });
    }

    const user = await findUserById(userId);
    if (!user || !user.isActive) {
      return sendApiError(res, {
        status: 401,
        message: 'User is inactive or deleted',
      });
    }

    (req as AuthRequest).userId = userId;
    (req as AuthRequest).sessionId = sessionId;
    (req as AuthRequest).role = user.role;
    next();
  } catch (err) {
    return sendApiError(res, {
      status: 401,
      message: 'Invalid or expired token',
    });
  }
};

export const validateRequest =
  <T extends z.ZodTypeAny>(schema: T) =>
  async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const parsed = await schema.parseAsync(req.body);

      // Important: overwrite body with validated + transformed data
      req.body = parsed;

      next();
    } catch (error) {
      if (error instanceof ZodError) {
        sendApiError(res, {
          status: 400,
          message: error.errors[0]?.message || 'Validation error',
          errors: error.flatten().fieldErrors,
        });
        return;
      }

      next(error);
    }
  };
