/**
 * form-solicitud.js
 * Sanitización defensiva, validación, construcción del payload y envío.
 *
 * Capas:
 *   1. Sanitización  — limpieza de strings antes de cualquier operación
 *   2. Validación    — reglas de negocio por campo
 *   3. Payload       — construcción del objeto JSON alineado con ContactFormSchema
 *   4. Transporte    — fetch con CSRF token hacia POST /api/contact
 *   5. UI            — feedback de éxito / error visible al usuario
 *
 * La sanitización en cliente NO sustituye la del backend; es una primera
 * línea de defensa y garantía de que el payload llega bien formado.
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
 * Elimina caracteres de control (U+0000–U+001F, U+007F) excepto
 * tabulación (\x09) y salto de línea (\x0A, \x0D) para el textarea.
 */
function stripControlChars(str, keepNewlines) {
  if (keepNewlines) {
    return str.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
  }
  return str.replace(/[\x00-\x1F\x7F]/g, '');
}

/** Trim + colapsa múltiples espacios en uno. */
function normalizeWs(str) {
  return str.trim().replace(/[ \t]{2,}/g, ' ');
}

/** Sanitización para campos de texto cortos. */
function sanitizeText(str, maxLen) {
  return normalizeWs(stripControlChars(stripTags(str), false)).slice(0, maxLen);
}

/** Sanitización de email: strip tags, control chars, lowercase, sin espacios. */
function sanitizeEmail(str) {
  return stripControlChars(stripTags(str), false)
    .trim()
    .toLowerCase()
    .replace(/\s/g, '')
    .slice(0, 254);
}

/**
 * Sanitización de teléfono: solo dígitos, +, espacios, guiones y paréntesis.
 */
function sanitizePhone(str) {
  return stripControlChars(stripTags(str), false)
    .replace(/[^\d\s+\-().]/g, '')
    .trim()
    .slice(0, 20);
}

/** Sanitización para el textarea largo. Conserva saltos de línea. */
function sanitizeTextarea(str, maxLen) {
  return stripControlChars(stripTags(str), true).trim().slice(0, maxLen);
}

// =============================================================================
// 2. VALIDACIÓN
// =============================================================================

const _EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const _PHONE_RE = /^\+?[\d][\d\s\-().]{5,18}[\d]$/;

const validators = {
  companyName(val) {
    if (!val || val.length < 2) return 'El nombre de la empresa es obligatorio (mínimo 2 caracteres).';
    return null;
  },

  companyEmail(val) {
    if (!val)                 return 'El correo de contacto es obligatorio.';
    if (!_EMAIL_RE.test(val)) return 'Introduce un correo electrónico válido.';
    return null;
  },

  phone(val) {
    if (!val)                 return 'El teléfono de contacto es obligatorio.';
    if (!_PHONE_RE.test(val)) return 'Introduce un teléfono válido (mínimo 7 dígitos).';
    return null;
  },

  isMember(val) {
    if (val === null) return 'Selecciona el tipo de solicitud.';
    return null;
  },

  message(val, isMember) {
    if (!isMember) return null;
    if (!val)      return 'Describe tu situación para que podamos ayudarte.';
    if (val.length < 20) return 'El mensaje debe tener al menos 20 caracteres.';
    return null;
  },

  privacyAccepted(checked) {
    if (!checked) return 'Debes aceptar los términos y condiciones para continuar.';
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

function _getField(input) {
  return input.closest('.form-field');
}

function clearFieldError(input) {
  const field = _getField(input);
  if (!field) return;
  field.classList.remove('form-field--error');
  field.querySelector('.form-field__error')?.remove();
}

function showFieldError(input, message) {
  const field = _getField(input);
  if (!field) return;
  clearFieldError(input);
  field.classList.add('form-field--error');
  const msg = document.createElement('p');
  msg.className = 'form-field__error';
  msg.setAttribute('role', 'alert');
  msg.textContent = message;
  field.appendChild(msg);
}

function clearGroupError(group) {
  group.classList.remove('form-group--error');
  group.querySelector('.form-group__error')?.remove();
}

function showGroupError(group, message) {
  clearGroupError(group);
  group.classList.add('form-group--error');
  const msg = document.createElement('p');
  msg.className = 'form-group__error';
  msg.setAttribute('role', 'alert');
  msg.textContent = message;
  group.appendChild(msg);
}

function clearAllErrors(form) {
  form.querySelectorAll('.form-field--error').forEach(el => el.classList.remove('form-field--error'));
  form.querySelectorAll('.form-field__error').forEach(el => el.remove());
  form.querySelectorAll('.form-group--error').forEach(el => el.classList.remove('form-group--error'));
  form.querySelectorAll('.form-group__error').forEach(el => el.remove());
}

// =============================================================================
// 4. FEEDBACK DE ESTADO (éxito / error)
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

/**
 * Obtiene el token CSRF del backend (GET /api/csrf-token).
 * El backend lo devuelve como cookie + JSON.
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
// 6. CONSTRUCCIÓN DEL PAYLOAD
// =============================================================================

/**
 * Construye el objeto JSON alineado con ContactFormSchema del backend.
 * Campos: company_name, company_email, country_code, phone,
 *         is_member (boolean), message, turnstile_token,
 *         privacy_accepted (boolean), website (honeypot, siempre vacío).
 */
function buildPayload(fields) {
  return {
    company_name:     fields.companyName,
    company_email:    fields.companyEmail,
    country_code:     fields.countryCode,
    phone:            fields.phone,
    is_member:        fields.isMember,
    message:          fields.message || '',
    turnstile_token:  fields.turnstileToken,
    privacy_accepted: true,
    website:          '',
  };
}

// =============================================================================
// 7. TRANSPORTE
// =============================================================================

async function submitPayload(payload, csrfToken) {
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;

  const res = await fetch('/api/contact', {
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
// 8. INICIALIZACIÓN
// =============================================================================

(function init() {
  const form = document.getElementById('form-solicitud');
  if (!form) return;

  const conditional  = document.getElementById('solicitud-mensaje');
  const feedbackEl   = document.getElementById('form-feedback');
  const submitBtn    = document.getElementById('form-submit-btn');

  const inputNombre   = form.querySelector('#empresa-nombre');
  const inputCorreo   = form.querySelector('#empresa-correo');
  const inputTelefono = form.querySelector('#empresa-telefono');
  const textareaMsg   = form.querySelector('#solicitud-detalle');
  const checkTerminos = form.querySelector('#acepta-terminos');

  // ── Toggle área condicional de mensaje (beneficiario) ──────────────────
  form.querySelectorAll('input[name="is_member"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
      const visible = this.value === 'true';
      conditional.classList.toggle('form-solicitud__conditional--visible', visible);
      conditional.setAttribute('aria-hidden', String(!visible));
    });
  });

  // ── Validación en blur ─────────────────────────────────────────────────
  inputNombre.addEventListener('blur', function () {
    const val = sanitizeText(this.value, 150);
    const err = validators.companyName(val);
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  inputCorreo.addEventListener('blur', function () {
    const val = sanitizeEmail(this.value);
    const err = validators.companyEmail(val);
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  inputTelefono.addEventListener('blur', function () {
    const val = sanitizePhone(this.value);
    const err = validators.phone(val);
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  // ── Submit ─────────────────────────────────────────────────────────────
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearAllErrors(form);
    hideFeedback(feedbackEl);

    // 1 — Sanitizar
    const companyName  = sanitizeText(inputNombre.value, 150);
    const companyEmail = sanitizeEmail(inputCorreo.value);
    const countryCode  = 'ES';
    const phone        = sanitizePhone(inputTelefono.value);

    const memberEl     = form.querySelector('input[name="is_member"]:checked');
    const isMember     = memberEl ? memberEl.value === 'true' : null;

    const message      = sanitizeTextarea(textareaMsg?.value ?? '', 2000);
    const privacyOk    = checkTerminos.checked;

    // Turnstile — el widget de Cloudflare rellena este input automáticamente
    const turnstileInput = form.querySelector('[name="cf-turnstile-response"]');
    const turnstileToken = turnstileInput?.value || '';

    // 2 — Validar
    let hasErrors = false;

    const errNombre = validators.companyName(companyName);
    if (errNombre) { showFieldError(inputNombre, errNombre); hasErrors = true; }

    const errCorreo = validators.companyEmail(companyEmail);
    if (errCorreo) { showFieldError(inputCorreo, errCorreo); hasErrors = true; }

    const errTelefono = validators.phone(phone);
    if (errTelefono) { showFieldError(inputTelefono, errTelefono); hasErrors = true; }

    const errMember = validators.isMember(isMember);
    if (errMember) {
      const radioGroup = form.querySelector('[role="radiogroup"]');
      if (radioGroup) showGroupError(radioGroup, errMember);
      hasErrors = true;
    }

    const errMessage = validators.message(message, isMember === true);
    if (errMessage && textareaMsg) { showFieldError(textareaMsg, errMessage); hasErrors = true; }

    const errPrivacy = validators.privacyAccepted(privacyOk);
    if (errPrivacy) { showFieldError(checkTerminos, errPrivacy); hasErrors = true; }

    const errTurnstile = validators.turnstile(turnstileToken);
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
      const firstErr = form.querySelector(
        '.form-field--error input, .form-field--error textarea, .form-group--error input'
      );
      firstErr?.focus();
      return;
    }

    // 3 — CSRF
    const csrfToken = await fetchCsrfToken();

    // 4 — Payload
    const payload = buildPayload({
      companyName, companyEmail, countryCode, phone,
      isMember, message, turnstileToken, privacyAccepted: true,
    });

    // 5 — Enviar
    submitBtn.disabled = true;
    submitBtn.textContent = 'Enviando…';

    try {
      await submitPayload(payload, csrfToken);

      form.reset();
      conditional.classList.remove('form-solicitud__conditional--visible');
      conditional.setAttribute('aria-hidden', 'true');
      // Reinicia el widget de Turnstile si la API está disponible (global inyectado por Cloudflare)
      if (typeof window.turnstile !== 'undefined') window.turnstile.reset();

      showFeedback(
        feedbackEl,
        'success',
        '¡Solicitud enviada! Nos pondremos en contacto contigo pronto.'
      );

    } catch (err) {
      showFeedback(
        feedbackEl,
        'error',
        err.message || 'Ha ocurrido un error al enviar el formulario. Inténtalo de nuevo.'
      );
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = 'Enviar formulario';
    }
  });
}());
