# services/email_service.py — Email helpers
from email.message import EmailMessage
import smtplib

from core.config import settings


def _send_email(to_email: str, subject: str, html_body: str) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg.set_content(html_body, subtype="html")

    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
        smtp.starttls()
        if settings.EMAIL_USER and settings.EMAIL_PASSWORD:
            smtp.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        smtp.send_message(msg)


def send_verification_email(to_email: str, user_name: str, verification_link: str, expiry_minutes: int) -> None:
    body = (
        f"<p>Hi {user_name},</p>"
        f"<p>Verify your account: <a href=\"{verification_link}\">Verify Account</a></p>"
        f"<p>This link expires in {expiry_minutes} minutes.</p>"
    )
    _send_email(to_email, "Verify your account", body)


def send_welcome_email(to_email: str, user_name: str, dashboard_link: str) -> None:
    body = (
        f"<p>Hi {user_name},</p>"
        f"<p>Welcome! Visit your dashboard: <a href=\"{dashboard_link}\">Open</a></p>"
    )
    _send_email(to_email, "Welcome", body)


def send_password_reset_email(to_email: str, user_name: str, reset_link: str, expiry_minutes: int) -> None:
    body = (
        f"<p>Hi {user_name},</p>"
        f"<p>Reset your password: <a href=\"{reset_link}\">Reset Password</a></p>"
        f"<p>This link expires in {expiry_minutes} minutes.</p>"
    )
    _send_email(to_email, "Password reset", body)
