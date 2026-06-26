import { Request, Response } from 'express';

export interface AuthRequest extends Request {
  userId?: string;
  sessionId?: string;
  role?: 'USER' | 'ADMIN';
}

export type ApiResponse = Response;
