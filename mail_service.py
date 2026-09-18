"""
app/services/mail_service.py

Email service responsible for sending verification emails, password reset
emails, and general notification emails over SMTP, using HTML templates.

Design notes:
    - SMTP delivery is fully async via `aiosmtplib`, so calls never block
      the FastAPI event loop.
    - HTML templates are rendered with Jinja2 when available. Built-in
      default templates are embedded so the service works out of the box;
      an optional `MAIL_TEMPLATES_DIR` env var lets you point to a directory
      of custom `.html` templates (e.g. "verification.html") to override them.
    - All configuration comes from environment variables.

This module intentionally contains NO API route or database logic.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Any, Final

logger = logging.getLogger(__name__)

try:
    import aiosmtplib
except ImportError as exc:  # pragma: no cover - environment guard
    raise ImportError(
        "The 'aiosmtplib' package is required for MailService. "
        "Install it with: pip install aiosmtplib"
    ) from exc

try:
    from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

    _JINJA_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    _JINJA_AVAILABLE = False


# --------------------------------------------------------------------------- #
# Exceptions
# --------------------------------------------------------------------------- #

class MailServiceError(Exception):
    """Base exception for all mail service related errors."""


class MailConfigError(MailServiceError):
    """Raised when required SMTP/email environment variables are missing."""


class MailSendError(MailServiceError):
    """Raised when an email fails to send via SMTP."""


class TemplateRenderError(MailServiceError):
    """Raised when an HTML email template fails to render."""


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #

@dataclass(frozen=True)
class EmailResult:
    """Outcome of an email send attempt."""

    to: str
    subject: str
    sent: bool

    def to_dict(self) -> dict[str, Any]:
        """Serialize the email result to a plain dict."""
        return {"to": self.to, "subject": self.subject, "sent": self.sent}


# --------------------------------------------------------------------------- #
# Built-in default templates (used when no custom template directory/
# template file is found, or Jinja2 is unavailable)
# --------------------------------------------------------------------------- #

_BASE_TEMPLATE: Final[str] = """\
<!DOCTYPE html>
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f4f5f7; padding: 24px;">
    <div style="max-width: 480px; margin: 0 auto; background: #ffffff; border-radius: 8px;
                padding: 32px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
      <h2 style="color: #1a1a1a;">{heading}</h2>
      <p style="color: #444444; font-size: 15px; line-height: 1.5;">{body}</p>
      {action_html}
      <p style="color: #999999; font-size: 12px; margin-top: 32px;">
        If you did not request this email, you can safely ignore it.
      </p>
    </div>
  </body>
</html>
"""

_ACTION_BUTTON_TEMPLATE: Final[str] = """\
<p style="margin: 24px 0;">
  <a href="{action_url}"
     style="background-color: #4f46e5; color: #ffffff; padding: 12px 20px;
            border-radius: 6px; text-decoration: none; font-size: 14px;">
    {action_label}
  </a>
</p>
"""

DEFAULT_TEMPLATES: Final[dict[str, str]] = {
    "verification": _BASE_TEMPLATE.format(
        heading="Verify your email address",
        body=(
            "Hi {{ name }}, thanks for signing up. Please confirm your email "
            "address to activate your account."
        ),
        action_html=_ACTION_BUTTON_TEMPLATE.format(
            action_url="{{ action_url }}", action_label="Verify Email"
        ),
    ),
    "password_reset": _BASE_TEMPLATE.format(
        heading="Reset your password",
        body=(
            "Hi {{ name }}, we received a request to reset your password. "
            "This link will expire shortly."
        ),
        action_html=_ACTION_BUTTON_TEMPLATE.format(
            action_url="{{ action_url }}", action_label="Reset Password"
        ),
    ),
    "notification": _BASE_TEMPLATE.format(
        heading="{{ title }}",
        body="Hi {{ name }}, {{ message }}",
        action_html=(
            "{% if action_url %}"
            + _ACTION_BUTTON_TEMPLATE.format(
                action_url="{{ action_url }}", action_label="{{ action_label }}"
            )
            + "{% endif %}"
        ),
    ),
}


# --------------------------------------------------------------------------- #
# Mail Service
# --------------------------------------------------------------------------- #

class MailService:
    """
    Service for sending transactional emails (verification, password reset,
    notifications) over SMTP using HTML templates.

    Configuration is read from environment variables:
        SMTP_HOST              (required)
        SMTP_PORT              (default: 587)
        SMTP_USERNAME          (required)
        SMTP_PASSWORD          (required)
        SMTP_USE_TLS           (default: "true")
        MAIL_FROM_ADDRESS      (required)
        MAIL_FROM_NAME         (default: "No Reply")
        MAIL_TEMPLATES_DIR     (optional, path to custom .html templates)

    Usage:
        service = MailService()
        await service.send_verification_email(
            to="user@example.com", name="Asha", action_url="https://app/verify?token=..."
        )
    """

    def __init__(
        self,
        smtp_host: str | None = None,
        smtp_port: int | None = None,
        smtp_username: str | None = None,
        smtp_password: str | None = None,
        use_tls: bool | None = None,
        from_address: str | None = None,
        from_name: str | None = None,
        templates_dir: str | None = None,
    ) -> None:
        """
        Initialize the MailService and validate SMTP configuration.

        Args:
            smtp_host: SMTP server hostname. Defaults to env SMTP_HOST.
            smtp_port: SMTP server port. Defaults to env SMTP_PORT or 587.
            smtp_username: SMTP auth username. Defaults to env SMTP_USERNAME.
            smtp_password: SMTP auth password. Defaults to env SMTP_PASSWORD.
            use_tls: Whether to use STARTTLS. Defaults to env SMTP_USE_TLS
                     ("true"/"false"), or True if unset.
            from_address: Sender email address. Defaults to env
                          MAIL_FROM_ADDRESS.
            from_name: Sender display name. Defaults to env MAIL_FROM_NAME
                       or "No Reply".
            templates_dir: Optional directory of custom Jinja2 HTML templates.
                           Defaults to env MAIL_TEMPLATES_DIR.

        Raises:
            MailConfigError: If required SMTP configuration is missing.
        """
        self._smtp_host = smtp_host or os.getenv("SMTP_HOST")
        self._smtp_port = int(smtp_port or os.getenv("SMTP_PORT", "587"))
        self._smtp_username = smtp_username or os.getenv("SMTP_USERNAME")
        self._smtp_password = smtp_password or os.getenv("SMTP_PASSWORD")

        use_tls_env = os.getenv("SMTP_USE_TLS", "true")
        self._use_tls = use_tls if use_tls is not None else use_tls_env.lower() == "true"

        self._from_address = from_address or os.getenv("MAIL_FROM_ADDRESS")
        self._from_name = from_name or os.getenv("MAIL_FROM_NAME", "No Reply")

        self._templates_dir = templates_dir or os.getenv("MAIL_TEMPLATES_DIR")

        self._validate_config()
        self._jinja_env = self._build_jinja_env()

    # ------------------------------------------------------------------- #
    # Configuration
    # ------------------------------------------------------------------- #

    def _validate_config(self) -> None:
        """
        Ensure all required SMTP/email environment variables are present.

        Raises:
            MailConfigError: If any required configuration value is missing.
        """
        missing = [
            name
            for name, value in (
                ("SMTP_HOST", self._smtp_host),
                ("SMTP_USERNAME", self._smtp_username),
                ("SMTP_PASSWORD", self._smtp_password),
                ("MAIL_FROM_ADDRESS", self._from_address),
            )
            if not value
        ]
        if missing:
            logger.error("Missing mail service environment variables: %s", missing)
            raise MailConfigError(
                f"Missing required mail environment variables: {', '.join(missing)}"
            )

    def _build_jinja_env(self) -> "Environment | None":
        """
        Build a Jinja2 environment for rendering templates, if Jinja2 is
        installed. A custom templates directory (if configured and it
        exists) takes precedence over built-in templates.

        Returns:
            A configured Jinja2 Environment, or None if Jinja2 is unavailable.
        """
        if not _JINJA_AVAILABLE:
            logger.warning(
                "Jinja2 is not installed; falling back to basic string "
                "substitution for email templates."
            )
            return None

        search_paths: list[str] = []
        if self._templates_dir and Path(self._templates_dir).is_dir():
            search_paths.append(self._templates_dir)

        loader = FileSystemLoader(search_paths) if search_paths else None
        return Environment(
            loader=loader,
            autoescape=select_autoescape(["html", "xml"]),
        )

    # ------------------------------------------------------------------- #
    # Template rendering
    # ------------------------------------------------------------------- #

    def _render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """
        Render an HTML email template with the given context.

        Resolution order:
            1. A custom template file (e.g. "verification.html") in
               MAIL_TEMPLATES_DIR, if configured and Jinja2 is available.
            2. The built-in default template string for `template_name`.

        Args:
            template_name: Logical template key (e.g. "verification",
                            "password_reset", "notification").
            context: Variables to substitute into the template.

        Returns:
            The rendered HTML string.

        Raises:
            TemplateRenderError: If rendering fails or the template is
                                  unknown.
        """
        if template_name not in DEFAULT_TEMPLATES:
            raise TemplateRenderError(f"Unknown email template: '{template_name}'.")

        try:
            if self._jinja_env is not None:
                if self._jinja_env.loader is not None:
                    try:
                        template = self._jinja_env.get_template(f"{template_name}.html")
                        return template.render(**context)
                    except TemplateNotFound:
                        logger.debug(
                            "Custom template '%s.html' not found; using default.",
                            template_name,
                        )
                template = self._jinja_env.from_string(DEFAULT_TEMPLATES[template_name])
                return template.render(**context)

            # Fallback: naive substitution when Jinja2 is unavailable.
            rendered = DEFAULT_TEMPLATES[template_name]
            for key, value in context.items():
                rendered = rendered.replace(f"{{{{ {key} }}}}", str(value))
            return rendered

        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to render email template '%s'.", template_name)
            raise TemplateRenderError(
                f"Failed to render template '{template_name}': {exc}"
            ) from exc

    # ------------------------------------------------------------------- #
    # Core sending
    # ------------------------------------------------------------------- #

    def _build_message(
        self, to: str, subject: str, html_body: str, text_body: str | None
    ) -> EmailMessage:
        """
        Construct a MIME EmailMessage ready for SMTP delivery.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            html_body: Rendered HTML content.
            text_body: Optional plain-text fallback content.

        Returns:
            A populated EmailMessage instance.
        """
        message = EmailMessage()
        message["From"] = f"{self._from_name} <{self._from_address}>"
        message["To"] = to
        message["Subject"] = subject
        message.set_content(text_body or "Please view this email in an HTML-capable client.")
        message.add_alternative(html_body, subtype="html")
        return message

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> EmailResult:
        """
        Send a raw HTML email over SMTP.

        Failures are caught, logged, and surfaced as a `MailSendError`
        rather than propagating raw SMTP exceptions, so calling code can
        handle mail failures gracefully (e.g. without failing an entire
        signup flow).

        Args:
            to: Recipient email address.
            subject: Email subject line.
            html_body: Rendered HTML content to send.
            text_body: Optional plain-text fallback content.

        Returns:
            An EmailResult describing the outcome.

        Raises:
            MailSendError: If the email fails to send.
        """
        if not to:
            raise MailSendError("Recipient email address ('to') is required.")

        message = self._build_message(to, subject, html_body, text_body)

        try:
            await aiosmtplib.send(
                message,
                hostname=self._smtp_host,
                port=self._smtp_port,
                username=self._smtp_username,
                password=self._smtp_password,
                start_tls=self._use_tls,
            )
        except Exception as exc:  # noqa: BLE001 - wrap all SMTP failures
            logger.exception("Failed to send email to=%s subject=%s.", to, subject)
            raise MailSendError(f"Failed to send email to '{to}': {exc}") from exc

        logger.info("Email sent successfully (to=%s, subject=%s).", to, subject)
        return EmailResult(to=to, subject=subject, sent=True)

    async def try_send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> EmailResult:
        """
        Best-effort variant of `send_email` that swallows failures instead
        of raising, returning an EmailResult with `sent=False` on error.
        Useful for non-critical notification emails where a delivery
        failure should not interrupt the calling workflow.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            html_body: Rendered HTML content to send.
            text_body: Optional plain-text fallback content.

        Returns:
            An EmailResult describing the outcome (sent True/False).
        """
        try:
            return await self.send_email(to, subject, html_body, text_body)
        except MailServiceError as exc:
            logger.warning("Suppressed mail failure for to=%s: %s", to, exc)
            return EmailResult(to=to, subject=subject, sent=False)

    # ------------------------------------------------------------------- #
    # High-level transactional emails
    # ------------------------------------------------------------------- #

    async def send_verification_email(
        self,
        to: str,
        name: str,
        action_url: str,
        subject: str = "Verify your email address",
    ) -> EmailResult:
        """
        Send an account verification email containing a confirmation link.

        Args:
            to: Recipient email address.
            name: Recipient's display name, used in the email greeting.
            action_url: The verification link the user should click.
            subject: Email subject line.

        Returns:
            An EmailResult describing the outcome.

        Raises:
            TemplateRenderError: If the template fails to render.
            MailSendError: If the email fails to send.
        """
        html_body = self._render_template(
            "verification", {"name": name, "action_url": action_url}
        )
        return await self.send_email(to=to, subject=subject, html_body=html_body)

    async def send_password_reset_email(
        self,
        to: str,
        name: str,
        action_url: str,
        subject: str = "Reset your password",
    ) -> EmailResult:
        """
        Send a password reset email containing a reset link.

        Args:
            to: Recipient email address.
            name: Recipient's display name, used in the email greeting.
            action_url: The password reset link the user should click.
            subject: Email subject line.

        Returns:
            An EmailResult describing the outcome.

        Raises:
            TemplateRenderError: If the template fails to render.
            MailSendError: If the email fails to send.
        """
        html_body = self._render_template(
            "password_reset", {"name": name, "action_url": action_url}
        )
        return await self.send_email(to=to, subject=subject, html_body=html_body)

    async def send_notification_email(
        self,
        to: str,
        name: str,
        title: str,
        message: str,
        action_url: str | None = None,
        action_label: str = "View Details",
        subject: str | None = None,
    ) -> EmailResult:
        """
        Send a general-purpose notification email.

        This is intended for non-critical, best-effort delivery (e.g.
        "your issue was resolved"), so failures are suppressed rather than
        raised — use `send_email` directly if you need strict failure
        propagation instead.

        Args:
            to: Recipient email address.
            name: Recipient's display name, used in the email greeting.
            title: Notification heading.
            message: Notification body text.
            action_url: Optional link for a call-to-action button.
            action_label: Label for the call-to-action button, if shown.
            subject: Email subject line. Defaults to `title` if not provided.

        Returns:
            An EmailResult describing the outcome (sent True/False).
        """
        html_body = self._render_template(
            "notification",
            {
                "name": name,
                "title": title,
                "message": message,
                "action_url": action_url,
                "action_label": action_label,
            },
        )
        return await self.try_send_email(
            to=to, subject=subject or title, html_body=html_body
        )