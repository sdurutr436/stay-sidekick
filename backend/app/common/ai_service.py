"""Servicio central de IA: LiteLLM, límites de uso y caché de system prompts."""

import logging
from datetime import date, datetime, timedelta, timezone

import litellm
from flask import current_app

from app.common.crypto import decrypt
from app.extensions import db
from app.h_vault_comunicaciones.model import AiUsageLog, SystemPrompt
from app.perfil.model import ConfiguracionIA

logger = logging.getLogger(__name__)

_prompt_cache: dict[str, str] = {}


def get_system_prompt(nombre: str, default: str) -> str:
    if nombre in _prompt_cache:
        return _prompt_cache[nombre]
    row = db.session.get(SystemPrompt, nombre)
    if row:
        _prompt_cache[nombre] = row.contenido
        return row.contenido
    _prompt_cache[nombre] = default
    return default


def invalidar_cache(nombre: str) -> None:
    _prompt_cache.pop(nombre, None)


def get_uso(empresa_id: str) -> dict:
    hoy = date.today()
    hace_7 = hoy - timedelta(days=6)

    uso_hoy = (
        db.session.query(AiUsageLog)
        .filter(AiUsageLog.empresa_id == empresa_id, AiUsageLog.fecha == hoy)
        .count()
    )
    uso_semana = (
        db.session.query(AiUsageLog)
        .filter(AiUsageLog.empresa_id == empresa_id, AiUsageLog.fecha >= hace_7)
        .count()
    )
    return {
        "uso_hoy": uso_hoy,
        "uso_semana": uso_semana,
        "limite_diario": current_app.config["AI_FREE_LIMIT_DAILY"],
        "limite_semanal": current_app.config["AI_FREE_LIMIT_WEEKLY"],
    }


def _get_config_ia(empresa_id: str) -> ConfiguracionIA | None:
    return db.session.query(ConfiguracionIA).filter_by(empresa_id=empresa_id).first()


def _is_byok(config_ia: ConfiguracionIA | None) -> bool:
    return config_ia is not None and config_ia.api_key_cifrada is not None


def _check_limits(empresa_id: str) -> None:
    hoy = date.today()
    hace_7 = hoy - timedelta(days=6)

    uso_hoy = (
        db.session.query(AiUsageLog)
        .filter(AiUsageLog.empresa_id == empresa_id, AiUsageLog.fecha == hoy)
        .count()
    )
    if uso_hoy >= current_app.config["AI_FREE_LIMIT_DAILY"]:
        raise ValueError("LIMIT_DAILY")

    uso_semana = (
        db.session.query(AiUsageLog)
        .filter(AiUsageLog.empresa_id == empresa_id, AiUsageLog.fecha >= hace_7)
        .count()
    )
    if uso_semana >= current_app.config["AI_FREE_LIMIT_WEEKLY"]:
        raise ValueError("LIMIT_WEEKLY")


def _registrar_uso(empresa_id: str, accion: str, tokens: int | None) -> None:
    db.session.add(AiUsageLog(empresa_id=empresa_id, accion=accion, tokens_usados=tokens))
    db.session.commit()


_FALLBACK_MODELS: dict[str, str] = {
    "gemini": "gemini/gemini-2.0-flash",
    "openai": "gpt-4o-mini",
    "claude": "claude-3-5-haiku-20241022",
}


def _litellm_params(config_ia: ConfiguracionIA | None) -> tuple[str, str | None]:
    if _is_byok(config_ia):
        api_key = decrypt(config_ia.api_key_cifrada)
        if config_ia.modelo:
            model = config_ia.modelo
        else:
            model = _FALLBACK_MODELS.get(config_ia.proveedor, current_app.config["AI_DEFAULT_MODEL"])
        return model, api_key

    model = current_app.config["AI_DEFAULT_MODEL"]
    api_key = current_app.config["AI_DEFAULT_API_KEY"] or None
    return model, api_key


def _call_litellm(
    model: str, api_key: str | None, system_prompt: str, user_message: str
) -> tuple[str, int | None]:
    kwargs: dict = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "timeout": 55,
    }
    if api_key:
        kwargs["api_key"] = api_key

    try:
        response = litellm.completion(**kwargs)
    except litellm.Timeout:
        raise TimeoutError("LiteLLM timeout")

    texto = response.choices[0].message.content.strip()
    try:
        tokens = response.usage.total_tokens
    except Exception:
        tokens = None
    return texto, tokens


_MEJORAR_DEFAULT = (
    "Eres un asistente experto en comunicación para alojamientos turísticos. "
    "Mejora el siguiente mensaje manteniendo el idioma original y un tono profesional "
    "y cercano. Conserva sin modificar todos los placeholders entre llaves "
    "({NOMBRE}, {APARTAMENTO}, etc.). Devuelve únicamente el mensaje mejorado, sin explicaciones."
)

_TRADUCIR_DEFAULT = (
    "Eres un traductor experto. Traduce el siguiente mensaje al idioma indicado. "
    "Conserva sin traducir todos los placeholders entre llaves "
    "({NOMBRE}, {APARTAMENTO}, etc.). Devuelve únicamente el mensaje traducido, sin explicaciones."
)


def mejorar(contenido: str, idioma: str, empresa_id: str) -> str:
    config_ia = _get_config_ia(empresa_id)
    if not _is_byok(config_ia):
        _check_limits(empresa_id)

    system_prompt = get_system_prompt("vault_mejorar", _MEJORAR_DEFAULT)
    model, api_key = _litellm_params(config_ia)
    user_message = f"Idioma: {idioma}\n\n{contenido}"
    texto, tokens = _call_litellm(model, api_key, system_prompt, user_message)
    _registrar_uso(empresa_id, "mejorar", tokens)
    return texto


def traducir(contenido: str, idioma_destino: str, empresa_id: str) -> str:
    config_ia = _get_config_ia(empresa_id)
    if not _is_byok(config_ia):
        _check_limits(empresa_id)

    system_prompt = get_system_prompt("vault_traducir", _TRADUCIR_DEFAULT)
    model, api_key = _litellm_params(config_ia)
    user_message = f"Idioma destino: {idioma_destino}\n\n{contenido}"
    texto, tokens = _call_litellm(model, api_key, system_prompt, user_message)
    _registrar_uso(empresa_id, "traducir", tokens)
    return texto
