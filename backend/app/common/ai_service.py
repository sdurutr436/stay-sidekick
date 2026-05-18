"""Servicio central de IA: LiteLLM, límites de uso y caché de system prompts."""

import logging
import math
from datetime import date, timedelta

import litellm
from flask import current_app

from app.common.crypto import decrypt
from app.common.notifications.discord import send_ai_observability_notification
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
    "gemini": "gemini/gemini-2.5-flash",
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


def _provider_name(model: str, config_ia: ConfiguracionIA | None) -> str:
    if config_ia and config_ia.proveedor:
        return config_ia.proveedor
    return model.split("/", 1)[0]


def _should_observe_system_ai(config_ia: ConfiguracionIA | None) -> bool:
    return not _is_byok(config_ia)


def _base_ai_details(
    accion: str,
    empresa_id: str,
    model: str,
    config_ia: ConfiguracionIA | None,
    user_message: str,
) -> dict[str, str | int]:
    return {
        "Accion": accion,
        "Empresa": empresa_id,
        "Modo": "system" if _should_observe_system_ai(config_ia) else "byok",
        "Proveedor": _provider_name(model, config_ia),
        "Modelo": model,
        "Chars entrada": len(user_message),
    }


def _notify_ai_event(
    title: str,
    accion: str,
    empresa_id: str,
    model: str,
    config_ia: ConfiguracionIA | None,
    user_message: str,
    *,
    severity: str = "warning",
    extra: dict[str, str | int] | None = None,
) -> None:
    if not _should_observe_system_ai(config_ia):
        return

    details = _base_ai_details(accion, empresa_id, model, config_ia, user_message)
    if extra:
        details.update(extra)
    send_ai_observability_notification(title, details, severity=severity)


def _threshold_hits(current: int, limit: int) -> bool:
    if limit <= 0:
        return False
    return current in {max(1, math.ceil(limit * 0.8)), limit}


def _notify_usage_thresholds(empresa_id: str, accion: str, config_ia: ConfiguracionIA | None) -> None:
    if not _should_observe_system_ai(config_ia):
        return

    uso = get_uso(empresa_id)
    if _threshold_hits(uso["uso_hoy"], uso["limite_diario"]):
        send_ai_observability_notification(
            "Uso alto de IA compartida (diario)",
            {
                "Accion": accion,
                "Empresa": empresa_id,
                "Uso hoy": uso["uso_hoy"],
                "Limite diario": uso["limite_diario"],
            },
            severity="warning" if uso["uso_hoy"] < uso["limite_diario"] else "error",
        )
    if _threshold_hits(uso["uso_semana"], uso["limite_semanal"]):
        send_ai_observability_notification(
            "Uso alto de IA compartida (semanal)",
            {
                "Accion": accion,
                "Empresa": empresa_id,
                "Uso semana": uso["uso_semana"],
                "Limite semanal": uso["limite_semanal"],
            },
            severity="warning" if uso["uso_semana"] < uso["limite_semanal"] else "error",
        )


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
        "num_retries": 0,
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

_MEJORAR_CLASICO_DEFAULT = (
    "Eres un asistente experto en comunicación para alojamientos turísticos. "
    "Mejora el siguiente mensaje en tono formal y profesional, usando usted. "
    "Mantén el idioma original. "
    "Conserva sin modificar todos los placeholders entre llaves "
    "({NOMBRE}, {APARTAMENTO}, {HORA_LLEGADA}, {HORA_SALIDA}, {PROTOCOLO_CHECKIN}, etc.). "
    "Devuelve únicamente el mensaje mejorado, sin explicaciones."
)

_MEJORAR_CERCANO_DEFAULT = (
    "Eres un asistente experto en comunicación para alojamientos turísticos. "
    "Mejora el siguiente mensaje con un tono cálido y cercano, tuteando al huésped. "
    "Mantén el idioma original. "
    "Conserva sin modificar todos los placeholders entre llaves "
    "({NOMBRE}, {APARTAMENTO}, {HORA_LLEGADA}, {HORA_SALIDA}, {PROTOCOLO_CHECKIN}, etc.). "
    "Devuelve únicamente el mensaje mejorado, sin explicaciones."
)

_MEJORAR_ENTUSIASTA_DEFAULT = (
    "Eres un asistente experto en comunicación para alojamientos turísticos. "
    "Mejora el siguiente mensaje con un tono muy acogedor y entusiasta, transmitiendo "
    "emoción genuina por recibir al huésped. Tutea con energía positiva. "
    "Mantén el idioma original. "
    "Conserva sin modificar todos los placeholders entre llaves "
    "({NOMBRE}, {APARTAMENTO}, {HORA_LLEGADA}, {HORA_SALIDA}, {PROTOCOLO_CHECKIN}, etc.). "
    "Devuelve únicamente el mensaje mejorado, sin explicaciones."
)

_MEJORAR_MINIMALISTA_DEFAULT = (
    "Eres un asistente experto en comunicación para alojamientos turísticos. "
    "Mejora el siguiente mensaje haciéndolo muy breve y directo, solo con la información esencial. "
    "Sin adornos ni frases de relleno. Mantén el idioma original. "
    "Conserva sin modificar todos los placeholders entre llaves "
    "({NOMBRE}, {APARTAMENTO}, {HORA_LLEGADA}, {HORA_SALIDA}, {PROTOCOLO_CHECKIN}, etc.). "
    "Devuelve únicamente el mensaje mejorado, sin explicaciones."
)

_TONO_PROMPTS: dict[str, tuple[str, str]] = {
    "clasico":     ("vault_mejorar_clasico",     _MEJORAR_CLASICO_DEFAULT),
    "cercano":     ("vault_mejorar_cercano",      _MEJORAR_CERCANO_DEFAULT),
    "entusiasta":  ("vault_mejorar_entusiasta",   _MEJORAR_ENTUSIASTA_DEFAULT),
    "minimalista": ("vault_mejorar_minimalista",  _MEJORAR_MINIMALISTA_DEFAULT),
}

_TRADUCIR_DEFAULT = (
    "Eres un traductor experto. Traduce el siguiente mensaje al idioma indicado. "
    "Conserva sin traducir todos los placeholders entre llaves "
    "({NOMBRE}, {APARTAMENTO}, etc.). Devuelve únicamente el mensaje traducido, sin explicaciones."
)


def _rate_limit_code(config_ia: ConfiguracionIA | None) -> str:
    return "RATE_LIMIT_BYOK" if _is_byok(config_ia) else "RATE_LIMIT_SYSTEM"


def mejorar(contenido: str, idioma: str, empresa_id: str, tono: str | None = None) -> str:
    config_ia = _get_config_ia(empresa_id)
    if not _is_byok(config_ia):
        _check_limits(empresa_id)

    if tono and tono in _TONO_PROMPTS:
        prompt_key, prompt_default = _TONO_PROMPTS[tono]
    else:
        prompt_key, prompt_default = "vault_mejorar", _MEJORAR_DEFAULT

    system_prompt = get_system_prompt(prompt_key, prompt_default)
    model, api_key = _litellm_params(config_ia)
    user_message = f"Idioma: {idioma}\n\n{contenido}"
    try:
        texto, tokens = _call_litellm(model, api_key, system_prompt, user_message)
    except litellm.RateLimitError:
        _notify_ai_event(
            "Rate limit del proveedor de IA compartido",
            "mejorar",
            empresa_id,
            model,
            config_ia,
            user_message,
            severity="warning",
        )
        raise ValueError(_rate_limit_code(config_ia))
    except TimeoutError:
        _notify_ai_event(
            "Timeout del proveedor de IA compartido",
            "mejorar",
            empresa_id,
            model,
            config_ia,
            user_message,
            severity="warning",
        )
        raise
    except Exception as exc:
        _notify_ai_event(
            "Fallo del proveedor de IA compartido",
            "mejorar",
            empresa_id,
            model,
            config_ia,
            user_message,
            severity="error",
            extra={"Excepcion": type(exc).__name__},
        )
        raise
    _registrar_uso(empresa_id, "mejorar", tokens)
    _notify_usage_thresholds(empresa_id, "mejorar", config_ia)
    return texto


def traducir(contenido: str, idioma_destino: str, empresa_id: str) -> str:
    config_ia = _get_config_ia(empresa_id)
    if not _is_byok(config_ia):
        _check_limits(empresa_id)

    system_prompt = get_system_prompt("vault_traducir", _TRADUCIR_DEFAULT)
    model, api_key = _litellm_params(config_ia)
    user_message = f"Idioma destino: {idioma_destino}\n\n{contenido}"
    try:
        texto, tokens = _call_litellm(model, api_key, system_prompt, user_message)
    except litellm.RateLimitError:
        _notify_ai_event(
            "Rate limit del proveedor de IA compartido",
            "traducir",
            empresa_id,
            model,
            config_ia,
            user_message,
            severity="warning",
        )
        raise ValueError(_rate_limit_code(config_ia))
    except TimeoutError:
        _notify_ai_event(
            "Timeout del proveedor de IA compartido",
            "traducir",
            empresa_id,
            model,
            config_ia,
            user_message,
            severity="warning",
        )
        raise
    except Exception as exc:
        _notify_ai_event(
            "Fallo del proveedor de IA compartido",
            "traducir",
            empresa_id,
            model,
            config_ia,
            user_message,
            severity="error",
            extra={"Excepcion": type(exc).__name__},
        )
        raise
    _registrar_uso(empresa_id, "traducir", tokens)
    _notify_usage_thresholds(empresa_id, "traducir", config_ia)
    return texto
