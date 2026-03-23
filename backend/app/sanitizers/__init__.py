"""DEPRECATED: usa app.common.sanitizers en su lugar."""
# Re-exports para compatibilidad temporal
from app.common.sanitizers.text import sanitize_text, sanitize_name  # noqa: F401
from app.common.sanitizers.phone import sanitize_phone  # noqa: F401
from app.common.sanitizers.email import sanitize_email  # noqa: F401
