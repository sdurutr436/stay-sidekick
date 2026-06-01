/**
 * cambio-password.js
 * Cambio obligatorio de contraseña al primer login.
 *
 * Capas (mismo patrón que form-login.js / form-solicitud.js):
 *   1. Sanitización defensiva   — limpia HTML/control chars antes de enviar
 *   2. Gestión de errores UI    — clase BEM .form-field--error + mensaje role="alert"
 *   3. Validación de fortaleza  — usa la fuente única window.SS_PASSWORD_RULES
 *   4. Render de fortaleza      — lista en vivo con criterios cumplidos / pendientes
 *   5. Transporte               — PUT /api/perfil/password con JWT Bearer
 *   6. Re-login                 — tras cambiar, el JWT antiguo queda inválido y
 *                                 se obtiene uno nuevo para no forzar al usuario
 *                                 a re-loguearse manualmente
 *   7. Inicialización           — guard del JWT, wiring del form, redirecciones
 *
 * Precondiciones del flujo:
 *   - Existe `ss_token` en localStorage o sessionStorage (si no → /login/).
 *   - El JWT trae `debe_cambiar_password: true` (si no → /menu directo).
 *   - El backend exige password actual + nueva + confirm (los 3) y aplica las
 *     mismas reglas de password-rules.js del lado servidor.
 *
 * Por qué hay re-login automático:
 *   El backend invalida el JWT activo tras cambiar la contraseña (rotación de
 *   credenciales). Si no hiciéramos re-login, el siguiente request del usuario
 *   en /menu reventaría con 401 y le obligaría a teclear su nueva contraseña.
 *   Hacemos el POST /api/auth/login con la nueva password en background y, si
 *   funciona, guardamos el nuevo token y le mandamos al panel.
 */

'use strict';

// =============================================================================
// 1. SANITIZACIÓN DEFENSIVA
// =============================================================================

/** Elimina todas las etiquetas HTML/XML del string. */
function stripTags(str) {
  return String(str).replace(/<[^>]*>/g, '');
}

/**
 * Elimina caracteres de control (U+0000–U+001F, U+007F).
 * La contraseña puede llevar cualquier carácter imprimible — sólo
 * eliminamos los de control.
 */
function stripControl(str) {
  return str.replace(/[\x00-\x1F\x7F]/g, '');
}

/** Sanitiza una contraseña: strip tags + control chars. Sin truncado ni hash en cliente. */
function sanitizePwd(str) {
  return stripControl(stripTags(String(str)));
}

// =============================================================================
// 2. GESTIÓN DE ERRORES EN UI (BEM .form-field--error)
// =============================================================================

/** Devuelve el contenedor BEM del campo dado su <input>. */
function _getField(input) {
  return input.closest('.form-field');
}

function clearFieldError(input) {
  const f = _getField(input);
  if (!f) return;
  f.classList.remove('form-field--error');
  f.querySelector('.form-field__error')?.remove();
}

function showFieldError(input, msg) {
  const f = _getField(input);
  if (!f) return;
  clearFieldError(input);
  f.classList.add('form-field--error');
  const p = document.createElement('p');
  p.className = 'form-field__error';
  p.setAttribute('role', 'alert');
  p.textContent = msg;
  f.appendChild(p);
}

function clearAllErrors(form) {
  form.querySelectorAll('.form-field--error').forEach(el => el.classList.remove('form-field--error'));
  form.querySelectorAll('.form-field__error').forEach(el => el.remove());
}

function showFeedback(el, msg) { el.textContent = msg; el.removeAttribute('hidden'); }
function hideFeedback(el)      { el.setAttribute('hidden', ''); el.textContent = ''; }

// =============================================================================
// 3. VALIDACIÓN DE FORTALEZA (fuente única en password-rules.js)
// =============================================================================

/**
 * Reglas compartidas con el backend (auth/password_rules.py) y la SPA Angular
 * (validators/password-strength.validator.ts). Se cargan desde el script
 * /assets/js/password-rules.js cargado antes que este archivo.
 */
const RULES = window.SS_PASSWORD_RULES;

/**
 * Valida que la confirmación coincida con la nueva contraseña.
 * @param {string} nueva   Contraseña nueva sanitizada.
 * @param {string} confirm Contraseña de confirmación sanitizada.
 * @returns {string|null}  Mensaje de error o null si todo OK.
 */
function validateConfirm(nueva, confirm) {
  if (!confirm)          return 'Debes confirmar la nueva contraseña.';
  if (nueva !== confirm) return 'Las contraseñas no coinciden.';
  return null;
}

// =============================================================================
// 4. RENDER DE LA LISTA DE FORTALEZA (live)
// =============================================================================

/**
 * Repinta la lista de criterios visible debajo del input "Nueva contraseña".
 * Cada criterio se marca con ✓ (cumplido) o ✗ (pendiente) y BEM modifier
 * --ok/--ko. El criterio MAX_LENGTH se oculta hasta que el usuario supera
 * el máximo (regla deliberada: no anticipar el límite superior).
 *
 * @param {HTMLElement} el    Contenedor <ul.password-strength>.
 * @param {string}      value Valor actual sanitizado del input.
 */
function renderStrengthList(el, value) {
  el.innerHTML = '';
  const exceedsMax = value.length > RULES.MAX_LENGTH;
  const items = exceedsMax ? RULES.CRITERIA.concat([RULES.MAX_CRITERION]) : RULES.CRITERIA;
  items.forEach(c => {
    const ok = c.test(value);
    const li = document.createElement('li');
    li.className = 'password-strength__item' + (ok ? ' password-strength__item--ok' : ' password-strength__item--ko');
    li.dataset.criterion = c.id;
    li.textContent = (ok ? '✓ ' : '✗ ') + c.label;
    el.appendChild(li);
  });
}

// =============================================================================
// 5. TRANSPORTE — PUT /api/perfil/password
// =============================================================================

/**
 * Envía el cambio de password al backend.
 * Requiere JWT Bearer válido (el backend valida y rota la credencial).
 *
 * @param {{ password_actual: string, password_nueva: string, password_confirm: string }} payload
 * @param {string} token JWT actual desde localStorage / sessionStorage.
 * @returns {Promise<object>} Cuerpo JSON de la respuesta del backend.
 * @throws {Error & { status?: number }} Si el backend responde !ok; el `status` se preserva.
 */
async function submitCambio(payload, token) {
  const res = await fetch('/api/perfil/password', {
    method: 'PUT',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': 'Bearer ' + token,
    },
    body: JSON.stringify(payload),
  });

  let body;
  try { body = await res.json(); } catch { body = {}; }

  if (!res.ok) {
    const msg = (body.errors && body.errors[0]) || body.error || `Error ${res.status}`;
    const err = new Error(msg);
    err.status = res.status;
    throw err;
  }
  return body;
}

// =============================================================================
// 6. RE-LOGIN AUTOMÁTICO TRAS CAMBIO
// =============================================================================

/**
 * Obtiene un JWT nuevo con la contraseña recién establecida.
 * Best-effort: si falla (red, CSRF, backend), devuelve null y el flujo
 * superior redirigirá al login para que el usuario teclee credenciales.
 *
 * @param {string} email     Email del JWT actual (claim `sub`).
 * @param {string} password  Contraseña nueva en claro (igual que la enviada en submitCambio).
 * @returns {Promise<string|null>} Nuevo JWT o null si no se pudo obtener.
 */
async function relogin(email, password) {
  let csrfToken = null;
  try {
    const r = await fetch('/api/csrf-token', { credentials: 'same-origin', headers: { 'Accept': 'application/json' } });
    if (r.ok) { const d = await r.json(); csrfToken = d.csrf_token || null; }
  } catch { /* sin CSRF — el backend devolverá 403 y caemos al fallback */ }

  const headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' };
  if (csrfToken) headers['X-CSRF-Token'] = csrfToken;

  const res = await fetch('/api/auth/login', {
    method: 'POST',
    credentials: 'same-origin',
    headers,
    body: JSON.stringify({ email, password, origen: 'web' }),
  });
  if (!res.ok) return null;
  const data = await res.json();
  return data.token || null;
}

// =============================================================================
// 7. INICIALIZACIÓN
// =============================================================================

(function init() {
  // ── Guard: el token debe existir y exigir cambio ─────────────────────────
  const token = localStorage.getItem('ss_token') || sessionStorage.getItem('ss_token');
  if (!token) { window.location.href = '/login/'; return; }

  let jwtEmail = null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (!payload.debe_cambiar_password) {
      // Si el usuario no necesita cambiar password, no debería estar aquí.
      window.location.href = '/menu';
      return;
    }
    jwtEmail = payload.sub || null;
  } catch {
    // Token malformado → al login a empezar de cero.
    window.location.href = '/login/';
    return;
  }

  const form = document.getElementById('form-cambio-pwd');
  if (!form) return;

  const inputActual  = form.querySelector('#pwd-actual');
  const inputNueva   = form.querySelector('#pwd-nueva');
  const inputConfirm = form.querySelector('#pwd-confirm');
  const strengthEl   = document.getElementById('pwd-strength');
  const feedbackEl   = document.getElementById('pwd-feedback');
  const exitoEl      = document.getElementById('pwd-exito');

  // Render inicial de la lista (todo en estado --ko).
  renderStrengthList(strengthEl, '');

  // ── Validación en tiempo real (input) ────────────────────────────────────
  inputNueva.addEventListener('input', function () {
    const v = sanitizePwd(this.value);
    renderStrengthList(strengthEl, v);
    const err = RULES.validate(v);
    // Sólo mostramos error si el usuario ya escribió algo; vacío es estado inicial.
    if (err && v.length > 0) showFieldError(this, err);
    else                     clearFieldError(this);
    // Si la confirmación ya tenía valor, re-validar la coincidencia.
    if (inputConfirm.value) {
      const errC = validateConfirm(v, sanitizePwd(inputConfirm.value));
      errC ? showFieldError(inputConfirm, errC) : clearFieldError(inputConfirm);
    }
  });

  inputConfirm.addEventListener('input', function () {
    const err = validateConfirm(sanitizePwd(inputNueva.value), sanitizePwd(this.value));
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  // ── Submit ──────────────────────────────────────────────────────────────
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearAllErrors(form);
    hideFeedback(feedbackEl);

    // 1 — Sanitizar
    const actual  = sanitizePwd(inputActual.value);
    const nueva   = sanitizePwd(inputNueva.value);
    const confirm = sanitizePwd(inputConfirm.value);

    // 2 — Validar (acumular errores para mostrarlos todos a la vez)
    let hasErrors = false;
    if (!actual) { showFieldError(inputActual, 'La contraseña actual es obligatoria.'); hasErrors = true; }

    const errNueva = RULES.validate(nueva);
    if (errNueva) { showFieldError(inputNueva, errNueva); hasErrors = true; }

    const errConfirm = validateConfirm(nueva, confirm);
    if (errConfirm) { showFieldError(inputConfirm, errConfirm); hasErrors = true; }

    if (hasErrors) { form.querySelector('.form-field--error input')?.focus(); return; }

    // 3 — Enviar al backend y, si todo OK, re-login + redirección
    const btn = document.getElementById('pwd-submit-btn');
    btn.disabled = true;
    btn.textContent = 'Guardando…';

    try {
      await submitCambio({ password_actual: actual, password_nueva: nueva, password_confirm: confirm }, token);

      // Token rotado server-side; obtenemos uno nuevo para no forzar re-login manual.
      const newToken = jwtEmail ? await relogin(jwtEmail, nueva) : null;
      if (newToken) {
        localStorage.setItem('ss_token', newToken);
      } else {
        // Re-login fallido: limpiamos los tokens viejos y redirigimos al login.
        localStorage.removeItem('ss_token');
        sessionStorage.removeItem('ss_token');
      }

      // Feedback visual breve antes de la redirección.
      form.hidden = true;
      exitoEl.hidden = false;
      setTimeout(() => { window.location.href = newToken ? '/menu' : '/login'; }, 2000);
    } catch (err) {
      // Mostramos el error en el campo "nueva" porque suele ser el motivo
      // (regla de fortaleza, password actual incorrecta, etc.).
      showFieldError(inputNueva, err.message || 'No se pudo cambiar la contraseña. Inténtalo de nuevo.');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Guardar nueva contraseña';
    }
  });
}());
