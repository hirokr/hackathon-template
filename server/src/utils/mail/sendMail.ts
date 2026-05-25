import nodemailer from 'nodemailer';
import nodemailerTransporter from '#src/config/nodemailer.config.ts';
import { VerificationEmailProps, WelcomeEmailProps } from '#src/types/email.js';
import {
  generateVerificationEmail,
  generateWelcomeEmail,
} from './mailTemplates.ts';

export const sendVerificationEmail = async ({
  to,
  userName,
  otpCode = '',
  verificationLink,
  expiryMinutes,
}: VerificationEmailProps & { to: string }) => {
  try {
    const html = generateVerificationEmail({
      userName,
      otpCode,
      verificationLink,
      expiryMinutes,
    });
    const mailer = await nodemailerTransporter();
    const info = await mailer.sendMail({
      from: process.env.EMAIL_USER,
      to,
      subject: 'Verification Code for Your Account',
      html,
    });
    if (process.env.NODE_ENV !== 'production') {
      console.log('[Mailer] Preview URL:', nodemailer.getTestMessageUrl(info));
    }
  } catch (error) {
    console.error('Error sending email:', error);
    throw new Error('Failed to send verification email');
  }
};

export const sendWelcomeEmail = async ({
  to,
  userName,
  dashboardLink,
}: WelcomeEmailProps & { to: string }) => {
  try {
    const html = generateWelcomeEmail({
      userName,
      dashboardLink,
    });
    const mailer = await nodemailerTransporter();
    const info = await mailer.sendMail({
      from: process.env.EMAIL_USER,
      to,
      subject: 'Welcome to Your Account',
      html,
    });
    if (process.env.NODE_ENV !== 'production') {
      console.log('[Mailer] Preview URL:', nodemailer.getTestMessageUrl(info));
    }
  } catch (error) {
    console.error('Error sending email:', error);
    throw new Error('Failed to send welcome email');
  }
};

export const sendPasswordResetEmail = async ({
  to,
  userName,
  expiryMinutes,
  resetLink,
  supportEmail = process.env.SUPPORT_EMAIL || 'support@tryora.com',
}: VerificationEmailProps & { to: string; resetLink: string }) => {
  try {
    const html = generateVerificationEmail({
      userName,
      verificationLink: resetLink,
      expiryMinutes,
      supportEmail,
    });
    const mailer = await nodemailerTransporter();
    const info = await mailer.sendMail({
      from: process.env.EMAIL_USER,
      to,
      subject: 'Password Reset Request',
      html,
    });
    if (process.env.NODE_ENV !== 'production') {
      console.log('[Mailer] Preview URL:', nodemailer.getTestMessageUrl(info));
    }
  } catch (error) {
    console.error('Error sending email:', error);
    throw new Error('Failed to send password reset email');
  }
};
