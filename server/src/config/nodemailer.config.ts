import nodemailer from 'nodemailer';

let transporter: nodemailer.Transporter;

const getNodemailerTransporter = async (): Promise<nodemailer.Transporter> => {
  if (transporter) return transporter;

  const emailUser = process.env.EMAIL_USER;
  const emailPass = process.env.EMAIL_PASS;

  if (!emailUser || !emailPass) {
    // No credentials — use Ethereal fake SMTP for dev/testing
    const testAccount = await nodemailer.createTestAccount();
    console.warn(
      '[Mailer] EMAIL_USER/EMAIL_PASS not set. Using Ethereal test account:',
      testAccount.user
    );
    console.warn(
      '[Mailer] Preview sent emails at https://ethereal.email/messages'
    );
    transporter = nodemailer.createTransport({
      host: 'smtp.ethereal.email',
      port: 587,
      secure: false,
      auth: {
        user: testAccount.user,
        pass: testAccount.pass,
      },
    });
  } else {
    transporter = nodemailer.createTransport({
      host: process.env.EMAIL_HOST || 'smtp.gmail.com',
      port: parseInt(process.env.EMAIL_PORT || '587'),
      secure: process.env.EMAIL_SECURE === 'true',
      auth: {
        user: emailUser,
        pass: emailPass,
      },
    });
  }

  return transporter;
};

export default getNodemailerTransporter;
