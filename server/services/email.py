"""Email sending service with console fallback for development."""

from __future__ import annotations

import logging
from email.message import EmailMessage

from server.config import get_settings

logger = logging.getLogger(__name__)


async def send_email(to: str, subject: str, body: str) -> None:
    settings = get_settings()

    if not settings.smtp_host:
        logger.warning(
            "[EMAIL FALLBACK] To: %s | Subject: %s\n%s",
            to, subject, body,
        )
        return

    import aiosmtplib

    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    await aiosmtplib.send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_user or None,
        password=settings.smtp_password or None,
        start_tls=settings.smtp_tls,
    )


async def send_verification_code(to: str, code: str) -> None:
    await send_email(
        to=to,
        subject="Sprint Undertaker — 이메일 인증 코드",
        body=(
            f"안녕하세요!\n\n"
            f"Sprint Undertaker 가입을 완료하려면 아래 인증 코드를 입력하세요.\n\n"
            f"  인증 코드: {code}\n\n"
            f"코드는 15분 동안 유효합니다.\n"
        ),
    )


async def send_password_reset_code(to: str, code: str) -> None:
    await send_email(
        to=to,
        subject="Sprint Undertaker — 비밀번호 재설정 코드",
        body=(
            f"안녕하세요!\n\n"
            f"비밀번호를 재설정하려면 아래 코드를 입력하세요.\n\n"
            f"  인증 코드: {code}\n\n"
            f"코드는 15분 동안 유효합니다.\n"
            f"본인이 요청하지 않았다면 이 메일을 무시하세요.\n"
        ),
    )
