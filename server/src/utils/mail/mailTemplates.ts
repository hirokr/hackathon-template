import { VerificationEmailProps, WelcomeEmailProps } from '#src/types/email.js';

export function generateVerificationEmail({
  userName = 'User',
  otpCode = '',
  verificationLink = '',
  expiryMinutes = 10,
  supportEmail = 'support@tryora.com',
  brandName = 'tryora',
}: VerificationEmailProps) {
  const year = new Date().getFullYear();

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>${brandName} Verification</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f6f8;padding:20px 0;">
    <tr>
      <td align="center">

        <table width="100%" cellpadding="0" cellspacing="0" border="0"
          style="max-width:600px;background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.05);">

          <!-- Header -->
          <tr>
            <td align="center" style="background-color:#111827;padding:24px;">
              <h1 style="color:#ffffff;margin:0;font-size:24px;font-weight:bold;">
                ${brandName}
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px 24px;color:#333333;">

              <p style="margin:0 0 16px 0;font-size:16px;">
                Hi ${userName},
              </p>

              <p style="margin:0 0 20px 0;font-size:15px;line-height:1.6;">
                Please use the verification details below to complete your request.
              </p>

              ${
                otpCode
                  ? `
              <!-- OTP Box -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:20px 0;">
                <tr>
                  <td align="center" style="background:#f3f4f6;padding:16px;border-radius:6px;">
                    <span style="font-size:28px;font-weight:bold;letter-spacing:6px;color:#111827;">
                      ${otpCode}
                    </span>
                  </td>
                </tr>
              </table>
              `
                  : ''
              }

              ${
                verificationLink
                  ? `
              <p style="text-align:center;color:#9ca3af;font-size:13px;margin:16px 0;">
                — OR —
              </p>

              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:20px 0;">
                <tr>
                  <td align="center">
                    <a href="${verificationLink}"
                      style="background-color:#2563eb;color:#ffffff;text-decoration:none;
                            padding:12px 24px;border-radius:6px;font-size:15px;
                            display:inline-block;font-weight:bold;">
                      Verify Account
                    </a>
                  </td>
                </tr>
              </table>
              `
                  : ''
              }

              <p style="margin:20px 0 0 0;font-size:13px;color:#6b7280;line-height:1.6;">
                This code and link will expire in ${expiryMinutes} minutes.
              </p>

              <p style="margin:16px 0 0 0;font-size:13px;color:#6b7280;">
                If you did not request this, you can safely ignore this email.
              </p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="background:#f9fafb;padding:20px;font-size:12px;color:#9ca3af;">
              © ${year} ${brandName}. All rights reserved.
              <br />
              Need help? Contact ${supportEmail}
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</body>
</html>
`;
}

export function generateWelcomeEmail({
  userName = 'User',
  dashboardLink = '#',
  supportEmail = 'support@tryora.com',
  brandName = 'tryora',
}: WelcomeEmailProps) {
  const year = new Date().getFullYear();

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Welcome to ${brandName}</title>
</head>
<body style="margin:0;padding:0;background-color:#f2f4f7;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="padding:40px 0;background-color:#f2f4f7;">
    <tr>
      <td align="center">

        <!-- Card Container -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
          style="max-width:620px;background:#ffffff;border-radius:10px;overflow:hidden;">

          <!-- Top Accent -->
          <tr>
            <td style="height:6px;background:linear-gradient(to right,#2563eb,#4f46e5);"></td>
          </tr>

          <!-- Header -->
          <tr>
            <td align="center" style="padding:36px 24px 12px 24px;">
              <h1 style="margin:0;font-size:26px;color:#111827;font-weight:bold;">
                Welcome to ${brandName}
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:0 40px 40px 40px;color:#374151;">

              <p style="font-size:16px;line-height:1.6;margin:24px 0 16px 0;">
                Hi ${userName},
              </p>

              <p style="font-size:15px;line-height:1.7;margin:0 0 18px 0;">
                Thank you for joining ${brandName}. Your account is now ready, and you’re all set to explore everything we’ve built for you.
              </p>

              <p style="font-size:15px;line-height:1.7;margin:0 0 28px 0;">
                Discover products, manage your orders, and enjoy a smooth shopping experience designed to be fast, secure, and reliable.
              </p>

              <!-- CTA Button -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:10px 0 30px 0;">
                <tr>
                  <td align="center">
                    <a href="${dashboardLink}"
                      style="background-color:#111827;color:#ffffff;text-decoration:none;
                            padding:14px 32px;border-radius:8px;
                            font-size:15px;font-weight:bold;
                            display:inline-block;">
                      Go to Dashboard
                    </a>
                  </td>
                </tr>
              </table>

              <p style="font-size:13px;line-height:1.6;color:#6b7280;margin:0;">
                Need help? Contact us at ${supportEmail}.
              </p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding:24px;background:#f9fafb;font-size:12px;color:#9ca3af;">
              © ${year} ${brandName}. All rights reserved.
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</body>
</html>
`;
}

export function generatePasswordResetEmail({
  userName = 'User',
  resetLink = '',
  expiryMinutes = 10,
  supportEmail = '',
}) {
  const year = new Date().getFullYear();
  const brandName = 'tryora';

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Password Reset Request</title>
</head>
<body style="margin:0;padding:0;background-color:#f4f6f8;font-family:Arial,Helvetica,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f6f8;padding:20px 0;">
    <tr>
      <td align="center">

        <table width="100%" cellpadding="0" cellspacing="0" border="0"
          style="max-width:600px;background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 4px 12px rgba(0,0,0,0.05);">

          <!-- Header -->
          <tr>
            <td align="center" style="background-color:#111827;padding:24px;">
              <h1 style="color:#ffffff;margin:0;font-size:24px;font-weight:bold;">
                Password Reset Request
              </h1>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px 24px;color:#333333;">

              <p style="margin:0 0 16px 0;font-size:16px;">
                Hi ${userName},
              </p>

              <p style="margin:0 0 20px 0;font-size:15px;line-height:1.6;">
                We received a request to reset your password. Click the button below to reset it.
              </p>  
              
              <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:16px 0;">
                <tr>
                  <td align="center">
                    <a href="${resetLink}"
                      style="background-color:#111827;color:#ffffff;text-decoration:none;
                            padding:14px 32px;border-radius:8px;
                            font-size:15px;font-weight:bold;
                            display:inline-block;">
                      Reset Password
                    </a>
                  </td>
                </tr>
              </table>

              <p style="margin:0 0 16px 0;font-size:14px;color:#6b7280;">
                This link will expire in ${expiryMinutes} minutes.
              </p>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding:24px;background:#f9fafb;font-size:12px;color:#9ca3af;">
              © ${year} ${brandName}. All rights reserved.
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>
</body>
</html>
`;
}
