# services/email_tasks.py — Celery tasks for email
from core.celery_app import celery_app
from services.email_service import (
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
)


@celery_app.task(name="email.send_verification")
def send_verification_email_task(to_email: str, user_name: str, verification_link: str, expiry_minutes: int) -> None:
    send_verification_email(to_email, user_name, verification_link, expiry_minutes)


@celery_app.task(name="email.send_welcome")
def send_welcome_email_task(to_email: str, user_name: str, dashboard_link: str) -> None:
    send_welcome_email(to_email, user_name, dashboard_link)


@celery_app.task(name="email.send_password_reset")
def send_password_reset_email_task(to_email: str, user_name: str, reset_link: str, expiry_minutes: int) -> None:
    send_password_reset_email(to_email, user_name, reset_link, expiry_minutes)
