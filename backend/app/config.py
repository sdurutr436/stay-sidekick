"""Configuración de la aplicación Flask cargada desde variables de entorno."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base — valores cargados de .env."""

    # Flask
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change-me")
    FLASK_ENV: str = os.environ.get("FLASK_ENV", "production")

    # CORS
    ALLOWED_ORIGINS: list[str] = [
        origin.strip()
        for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
        if origin.strip()
    ]

    # Cloudflare Turnstile
    TURNSTILE_SECRET_KEY: str = os.environ.get("TURNSTILE_SECRET_KEY", "")
    TURNSTILE_VERIFY_URL: str = os.environ.get(
        "TURNSTILE_VERIFY_URL",
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
    )

    # Gmail SMTP
    GMAIL_USER: str = os.environ.get("GMAIL_USER", "")
    GMAIL_APP_PASSWORD: str = os.environ.get("GMAIL_APP_PASSWORD", "")
    MAIL_RECIPIENT: str = os.environ.get("MAIL_RECIPIENT", "")

    # Discord
    DISCORD_WEBHOOK_URL: str = os.environ.get("DISCORD_WEBHOOK_URL", "")

    # JWT (para rutas autenticadas del panel)
    JWT_SECRET_KEY: str = os.environ.get("JWT_SECRET_KEY", "change-me-jwt")
    JWT_ACCESS_TOKEN_HOURS: int = int(os.environ.get("JWT_ACCESS_TOKEN_HOURS", "1"))

    # Rate limiting
    RATE_LIMIT_CONTACT: str = os.environ.get("RATE_LIMIT_CONTACT", "5/hour")
