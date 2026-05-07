/**
 * form-contacto.js
 * Sanitización, validación, construcción del payload y envío.
 *
 * Capas:
 *   1. Sanitización  — limpieza de strings antes de cualquier operación
 *   2. Validación    — reglas por campo
 *   3. CSRF          — obtención del token desde /api/csrf-token
 *   4. Transporte    — fetch con CSRF token hacia POST /api/contacto
 *
 * Protecciones anti-spam:
 *   · Honeypot       — campo oculto "website" que los bots rellenan
 *   · Turnstile      — captcha de Cloudflare verificado en servidor
 *   · CSRF           — Double-Submit Cookie
 *   · Rate limiting  — 10/hour en el backend
 */

'use strict';

// =============================================================================
// 1. SANITIZACIÓN
// =============================================================================

function stripTags(str) {
  return String(str).replace(/<[^>]*>/g, '');
}

function stripControlChars(str, keepNewlines) {
  if (keepNewlines) {
    return str.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
  }
  return str.replace(/[\x00-\x1F\x7F]/g, '');
}

function normalizeWs(str) {
  return str.trim().replace(/[ \t]{2,}/g, ' ');
}

function sanitizeText(str, maxLen) {
  return normalizeWs(stripControlChars(stripTags(str), false)).slice(0, maxLen);
}

function sanitizeEmail(str) {
  return stripControlChars(stripTags(str), false)
    .trim()
    .toLowerCase()
    .replace(/\s/g, '')
    .slice(0, 254);
}

function sanitizeTextarea(str, maxLen) {
  return stripControlChars(stripTags(str), true).trim().slice(0, maxLen);
}

// =============================================================================
// 2. VALIDACIÓN
// =============================================================================

const _EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const validators = {
  nombre(val) {
    if (!val) return 'El nombre es obligatorio.';
    if (val.length > 100) return 'El nombre no puede superar los 100 caracteres.';
    return null;
  },
  email(val) {
    if (!val) return 'El correo electrónico es obligatorio.';
    if (!_EMAIL_RE.test(val)) return 'Introduce un correo electrónico válido.';
    return null;
  },
  mensaje(val) {
    if (!val) return 'El mensaje es obligatorio.';
    if (val.length < 10) return 'El mensaje debe tener al menos 10 caracteres.';
    if (val.length > 2000) return 'El mensaje no puede superar los 2000 caracteres.';
    return null;
  },
  turnstile(token) {
    if (!token) return 'Completa la verificación de seguridad.';
    return null;
  },
};

// =============================================================================
// 3. GESTIÓN DE ERRORES EN UI
// =============================================================================

function clearFieldError(input) {
  const field = input.closest('.form-field');
  if (!field) return;
  field.classList.remove('form-field--error');
  field.querySelector('.form-field__error')?.remove();
}

function showFieldError(input, message) {
  const field = input.closest('.form-field');
  if (!field) return;
  clearFieldError(input);
  field.classList.add('form-field--error');
  const msg = document.createElement('p');
  msg.className = 'form-field__error';
  msg.setAttribute('role', 'alert');
  msg.textContent = message;
  field.appendChild(msg);
}

function clearAllErrors(form) {
  form.querySelectorAll('.form-field--error').forEach(el => el.classList.remove('form-field--error'));
  form.querySelectorAll('.form-field__error').forEach(el => el.remove());
}

// =============================================================================
// 4. FEEDBACK DE ESTADO
// =============================================================================

function showFeedback(feedbackEl, type, message) {
  feedbackEl.textContent = message;
  feedbackEl.className = 'form-solicitud__feedback form-solicitud__feedback--' + type;
  feedbackEl.removeAttribute('hidden');
}

function hideFeedback(feedbackEl) {
  feedbackEl.setAttribute('hidden', '');
  feedbackEl.textContent = '';
  feedbackEl.className = 'form-solicitud__feedback';
}

// =============================================================================
// 5. CSRF
// =============================================================================

async function fetchCsrfToken() {
  try {
    const res = await fetch('/api/csrf-token', {
      method: 'GET',
      credentials: 'same-origin',
      headers: { 'Accept': 'application/json' },
    });
    if (!res.ok) return null;
    const data = await res.json();
    return (typeof data.csrf_token === 'string' && data.csrf_token) ? data.csrf_token : null;
  } catch {
    return null;
  }
}

// =============================================================================
// 6. ENVÍO
// =============================================================================

async function submitContacto(payload, csrfToken) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;

  const res = await fetch('/api/contacto', {
    method: 'POST',
    credentials: 'same-origin',
    headers,
    body: JSON.stringify(payload),
  });

  let body;
  try { body = await res.json(); } catch { body = {}; }

  if (!res.ok) {
    const errMsg = (body.errors && body.errors[0]) || `Error ${res.status}`;
    throw new Error(errMsg);
  }

  return body;
}

// =============================================================================
// 7. INICIALIZACIÓN
// =============================================================================

(function init() {
  const form = document.getElementById('form-contacto');
  if (!form) return;

  const feedbackEl  = document.getElementById('contacto-feedback');
  const submitBtn   = document.getElementById('contacto-submit-btn');

  const nombreInput  = form.querySelector('#contacto-nombre');
  const emailInput   = form.querySelector('#contacto-email');
  const empresaInput = form.querySelector('#contacto-empresa');
  const mensajeInput = form.querySelector('#contacto-mensaje');

  // ── Validación en blur ──────────────────────────────────────────────────
  nombreInput?.addEventListener('blur', function () {
    const err = validators.nombre(sanitizeText(this.value, 100));
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  emailInput?.addEventListener('blur', function () {
    const err = validators.email(sanitizeEmail(this.value));
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  mensajeInput?.addEventListener('blur', function () {
    const err = validators.mensaje(sanitizeTextarea(this.value, 2000));
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  // ── Submit ──────────────────────────────────────────────────────────────
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearAllErrors(form);
    hideFeedback(feedbackEl);

    const nombre  = sanitizeText(nombreInput?.value  ?? '', 100);
    const email   = sanitizeEmail(emailInput?.value  ?? '');
    const empresa = sanitizeText(empresaInput?.value ?? '', 150);
    const mensaje = sanitizeTextarea(mensajeInput?.value ?? '', 2000);

    // Turnstile — el widget rellena este input automáticamente
    const turnstileInput = form.querySelector('[name="cf-turnstile-response"]');
    const turnstileToken = turnstileInput?.value || '';

    let hasErrors = false;

    const errNombre  = validators.nombre(nombre);
    const errEmail   = validators.email(email);
    const errMensaje = validators.mensaje(mensaje);
    const errTurnstile = validators.turnstile(turnstileToken);

    if (errNombre)  { showFieldError(nombreInput,  errNombre);  hasErrors = true; }
    if (errEmail)   { showFieldError(emailInput,   errEmail);   hasErrors = true; }
    if (errMensaje) { showFieldError(mensajeInput, errMensaje); hasErrors = true; }

    if (errTurnstile) {
      const tsWrapper = form.querySelector('.cf-turnstile');
      if (tsWrapper) {
        const msg = document.createElement('p');
        msg.className = 'form-field__error';
        msg.setAttribute('role', 'alert');
        msg.textContent = errTurnstile;
        tsWrapper.after(msg);
      }
      hasErrors = true;
    }

    if (hasErrors) {
      form.querySelector('.form-field--error input, .form-field--error textarea')?.focus();
      return;
    }

    submitBtn.disabled = true;

    try {
      const csrfToken = await fetchCsrfToken();
      await submitContacto({
        nombre,
        email,
        empresa,
        mensaje,
        turnstile_token: turnstileToken,
        website: '',  // honeypot siempre vacío desde cliente legítimo
      }, csrfToken);

      form.reset();
      if (typeof window.turnstile !== 'undefined') window.turnstile.reset();
      form.hidden = true;
      document.getElementById('form-contacto-exito').hidden = false;
    } catch (err) {
      showFeedback(feedbackEl, 'error', err.message || 'Error al enviar el mensaje. Inténtalo de nuevo.');
    } finally {
      submitBtn.disabled = false;
    }
  });

  form.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('input', () => clearFieldError(input));
  });
}());
