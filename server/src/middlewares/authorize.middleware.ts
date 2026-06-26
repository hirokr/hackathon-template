import { NextFunction, Response } from 'express';
import { AuthRequest } from '#src/types/authRequest.js';
import { sendApiError } from '#src/utils/api-response.ts';

type Role = 'USER' | 'ADMIN';

export const requireRole =
  (...roles: Role[]) =>
  (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.role) {
      return sendApiError(res, { status: 401, message: 'Unauthorized' });
    }

    if (!roles.includes(req.role)) {
      return sendApiError(res, { status: 403, message: 'Forbidden' });
    }

    next();
  };
