import {
  changePassword,
  deleteAccount,
  forgotPassword,
  getProfile,
  resendVerificationEmail,
  resetPassword,
  updateUserProfileData,
  verifyEmail,
} from '#src/controllers/user.controller.ts';
import { authMiddleware } from '#src/middlewares/authenticate.middleware.ts';
import { Router } from 'express';

const router = Router();
router.post('/reset-password', resetPassword);
router.post('/forgot-password', forgotPassword);
router.post('/verify-email', verifyEmail);
router.post('/resend-verification-email', resendVerificationEmail);
router.use(authMiddleware);
router.get('/me', getProfile);
router.patch('/me', updateUserProfileData);
router.post('/change-password', changePassword);
router.delete('/delete-account', deleteAccount);

export default router;
