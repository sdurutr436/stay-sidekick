---
id: modulos-h
title: Módulos h_* (herramientas operativas)
sidebar_position: 4
description: Qué hace cada herramienta operativa (mapa de calor, vault IA, notificaciones tardías, sincronizador, maestro).
---

# Módulos `h_*` — herramientas operativas

Los paquetes `h_*` son las **herramientas operacionales** que Stay Sidekick aporta sobre el PMS. Cada uno es **autocontenido**: tiene su Blueprint, su `service.py`, su lógica de dominio y, si toca, su cliente externo. Esto evita acoplamiento y permite añadir herramientas nuevas sin tocar las existentes.

## Mapa global

| Paquete | Ruta pública | Persistencia | Integraciones |
|---------|--------------|--------------|---------------|
| [`h_maestro_apartamentos`](#h_maestro_apartamentos) | `/api/maestro-apartamentos` | Sí (apartamentos por empresa) | Smoobu (opt.), XLSX import |
| [`h_mapa_de_calor`](#h_mapa_de_calor) | `/api/heatmap` | **No** — en memoria | PMS o XLSX |
| [`h_notificaciones_tardias`](#h_notificaciones_tardias) | `/api/notificaciones-tardias` | Plantillas + reglas | PMS o XLSX |
| [`h_sincronizador_contactos`](#h_sincronizador_contactos) | `/api/contactos` | Tokens OAuth (cifrados) | Google People API |
| [`h_vault_comunicaciones`](#h_vault_comunicaciones) | `/api/vault` | Plantillas + uso IA | OpenAI / Gemini / Claude |

## h_maestro_apartamentos

Catálogo centralizado del inventario sobre el que operan el resto de módulos. Permite:

- Alta, edición y **baja lógica** (no destructiva) por empresa.
- **Sincronización con PMS** — Smoobu como referencia, arquitectura extensible vía `normalizador_pms`.
- **Importación masiva XLSX** con vista previa antes de persistir.

## h_mapa_de_calor

Visualización diaria de entradas y salidas para anticipar picos operativos.

- **Procesado 100 % en memoria** — alineado con RGPD; los huéspedes no se guardan en BD.
- **Doble origen**: PMS (Smoobu) o XLSX subido.
- **Umbrales configurables por empresa** — adapta el semáforo al volumen real de cada cliente.

## h_notificaciones_tardias

Detección automática de check-ins del día y plantillas de mensaje para reducir tiempo de respuesta.

- **CRUD de plantillas** editables por la empresa.
- **Hora de corte** y reglas configurables (a partir de qué hora se considera tardío).
- **Doble origen**: PMS o XLSX.

## h_sincronizador_contactos

Sincronización PMS → Google Contacts con OAuth 2.0.

- Conexión vía **OAuth 2.0 + Google People API**.
- Agrupa huéspedes por nombre y teléfono.
- **Tokens cifrados** en BD con Fernet.
- **Exportación CSV** como fallback de auditoría o cargas externas.

## h_vault_comunicaciones

Vault de plantillas de comunicación con asistente IA opcional.

- **CRUD completo de plantillas** con borrado lógico (`PlantillaVault`).
- **Asistente IA** opcional: mejora redacción y traduce.
- **Free tier compartido** con `AiUsageLog` y límites por empresa (`AI_FREE_LIMIT_DAILY/WEEKLY`).
- **BYOK (Bring Your Own Key)** — la empresa puede aportar su propia API key, cifrada en BD.
- **System prompts editables** desde el admin sin tocar código.
