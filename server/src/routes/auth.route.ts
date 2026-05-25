import { Router } from 'express';
import {
  googleAuth,
  googleAuthCallback,
  googleAuthFailure,
  refresh,
  signin,
  signout,
  signup,
} from '#src/controllers/auth.controller.ts';
import {
  authMiddleware,
  validateRequest,
} from '#src/middlewares/authenticate.middleware.ts';
import {
  SigninFormSchema,
  SignupFormSchema,
} from '#src/validations/auth.validation.ts';

const router = Router();

router.get('/google', googleAuth);
router.get('/google/callback', googleAuthCallback);
router.get('/google/failure', googleAuthFailure);
router.post('/signup', validateRequest(SignupFormSchema), signup);
router.post('/signin', validateRequest(SigninFormSchema), signin);
router.get('/refresh', refresh);
router.get('/signout', authMiddleware, signout);

export default router;
