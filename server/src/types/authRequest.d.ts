import { Request, Response } from 'express';

export interface AuthRequest extends Request {
  userId?: string;
  sessionId?: string;
}

export type Response = Response;
