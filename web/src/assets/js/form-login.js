/**
 * form-login.js
 * Sanitización defensiva, validación, construcción del payload y envío.
 *
 * Capas:
 *   1. Sanitización  — limpieza de strings antes de cualquier operación
 *   2. Validación    — reglas por campo (email + password)
 *   3. Payload       — construcción del objeto JSON limpio
 *   4. Transporte    — fetch con CSRF token; JWT gestionado por el backend
 */

'use strict';

// =============================================================================
// 1. SANITIZACIÓN
// =============================================================================

/** Elimina todas las etiquetas HTML/XML del string. */
function stripTags(str) {
  return String(str).replace(/<[^>]*>/g, '');
}

/**
 * Elimina caracteres de control (U+0000–U+001F, U+007F).
 * La contraseña puede contener cualquier carácter imprimible —
 * solo eliminamos los de control, nunca truncamos ni normalizamos.
 */
function stripControlChars(str) {
  return str.replace(/[\x00-\x1F\x7F]/g, '');
}

/**
 * Sanitización de email: strip tags, control chars, lowercase, sin espacios.
 * RFC 5321 → máx. 254 caracteres.
 */
function sanitizeEmail(str) {
  return stripControlChars(stripTags(str))
    .trim()
    .toLowerCase()
    .replace(/\s/g, '')
    .slice(0, 254);
}

/**
 * Sanitización de contraseña.
 * Preserva espacios internos (válidos en passwords), elimina solo:
 *  - etiquetas HTML
 *  - caracteres de control
 * NO se normaliza, trunca (más de 128 chars sería anomalía) ni hashea en cliente.
 */
function sanitizePassword(str) {
  return stripControlChars(stripTags(String(str))).slice(0, 128);
}

// =============================================================================
// 2. VALIDACIÓN
// =============================================================================

const _EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

const validators = {
  email(val) {
    if (!val)                 return 'El correo electrónico es obligatorio.';
    if (!_EMAIL_RE.test(val)) return 'Introduce un correo electrónico válido.';
    return null;
  },

  password(val) {
    if (!val)          return 'La contraseña es obligatoria.';
    if (val.length < 8) return 'La contraseña debe tener al menos 8 caracteres.';
    return null;
  },
};

// =============================================================================
// 3. GESTIÓN DE ERRORES EN UI
// =============================================================================

function _getField(input) {
  return input.closest('.form-field');
}

function clearFieldError(input) {
  const field = _getField(input);
  if (!field) return;
  field.classList.remove('form-field--error');
  field.querySelector('.form-field__error')?.remove();
  input.removeAttribute('aria-describedby');
}

function showFieldError(input, message) {
  const field = _getField(input);
  if (!field) return;
  clearFieldError(input);
  field.classList.add('form-field--error');
  const errorId = (input.id || 'field') + '-error';
  const msg = document.createElement('p');
  msg.className = 'form-field__error';
  msg.setAttribute('role', 'alert');
  msg.id = errorId;
  msg.textContent = message;
  field.appendChild(msg);
  input.setAttribute('aria-describedby', errorId);
}

function clearAllErrors(form) {
  form.querySelectorAll('.form-field--error').forEach(el => el.classList.remove('form-field--error'));
  form.querySelectorAll('.form-field__error').forEach(el => el.remove());
}

// =============================================================================
// 4. CSRF
// =============================================================================

/**
 * Obtiene el token CSRF del backend.
 * GET /api/csrf-token → { csrf_token: "..." }
 */
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
// 5. CONSTRUCCIÓN DEL PAYLOAD
// =============================================================================

/**
 * Construye el objeto JSON limpio listo para el backend.
 * La contraseña se envía en claro sobre HTTPS — el backend la verifica
 * contra el hash almacenado; nunca se hashea en cliente.
 *
 * @param {{ email: string, password: string }} fields
 * @returns {{ email: string, password: string, origen: string }}
 */
function buildPayload(fields) {
  return {
    email:    fields.email,
    password: fields.password,
    origen:   'web',
  };
}

// =============================================================================
// 6. TRANSPORTE
// =============================================================================

/**
 * Envía el payload de login.
 * El backend responde con { ok, token } y el frontend guarda el JWT
 * en localStorage bajo la clave 'ss_token' para usarlo en la SPA Angular.
 *
 * @param {object} payload
 * @param {string|null} csrfToken
 */
async function submitPayload(payload, csrfToken) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;

  const res = await fetch('/api/auth/login', {
    method: 'POST',
    credentials: 'same-origin',
    headers,
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    let errMsg = `Error ${res.status}`;
    try {
      const body = await res.json();
      if (body.message) errMsg = body.message;
      else if (Array.isArray(body.errors) && body.errors.length) errMsg = body.errors[0];
    } catch { /* noop */ }
    throw new Error(errMsg);
  }

  return res.json();
}

// =============================================================================
// 7. INICIALIZACIÓN
// =============================================================================

(function initAccesoAlert() {
  if (new URLSearchParams(window.location.search).get('acceso') !== 'requerido') return;

  const alert  = document.getElementById('acceso-alert');
  const close  = document.getElementById('acceso-alert-close');
  if (!alert) return;

  alert.removeAttribute('hidden');

  const hide = () => alert.setAttribute('hidden', '');
  close?.addEventListener('click', hide);
  setTimeout(hide, 6000);
}());

(function init() {
  const form = document.getElementById('form-login');
  if (!form) return;

  const inputEmail    = form.querySelector('#login-email');
  const inputPassword = form.querySelector('#login-password');

  // ── Validación en blur ──────────────────────────────────────────────────
  inputEmail.addEventListener('blur', function () {
    const val = sanitizeEmail(this.value);
    const err = validators.email(val);
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  inputPassword.addEventListener('blur', function () {
    const val = sanitizePassword(this.value);
    const err = validators.password(val);
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  // ── Submit ──────────────────────────────────────────────────────────────
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearAllErrors(form);

    // 1 — Sanitizar
    const email    = sanitizeEmail(inputEmail.value);
    const password = sanitizePassword(inputPassword.value);

    // 2 — Validar
    let hasErrors = false;

    const errEmail = validators.email(email);
    if (errEmail) { showFieldError(inputEmail, errEmail); hasErrors = true; }

    const errPassword = validators.password(password);
    if (errPassword) { showFieldError(inputPassword, errPassword); hasErrors = true; }

    if (hasErrors) {
      form.querySelector('.form-field--error input')?.focus();
      return;
    }

    // 3 — CSRF
    const csrfToken = await fetchCsrfToken();

    // 4 — Payload
    const payload = buildPayload({ email, password });

    // 5 — Enviar
    const submitBtn = form.querySelector('[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.setAttribute('aria-busy', 'true');
    submitBtn.textContent = 'Entrando…';

    try {
      const data = await submitPayload(payload, csrfToken);
      if (data.token) {
        localStorage.setItem('ss_token', data.token);
        window.location.href = data.debe_cambiar_password ? '/cambio-password' : '/menu';
      }
    } catch (err) {
      // Muestra el error del backend en el campo email (es el punto de entrada)
      showFieldError(inputEmail, err.message || 'Credenciales incorrectas.');
    } finally {
      submitBtn.disabled = false;
      submitBtn.removeAttribute('aria-busy');
      submitBtn.textContent = 'Iniciar sesión';
    }
  });
}());
