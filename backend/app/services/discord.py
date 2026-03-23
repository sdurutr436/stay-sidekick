"""DEPRECATED: usa app.common.notifications.discord en su lugar."""
from app.common.notifications.discord import send_discord_notification  # noqa: F401

__all__ = ["send_discord_notification"]
