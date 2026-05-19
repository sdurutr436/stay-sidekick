'use strict';

function stripTags(str)         { return String(str).replace(/<[^>]*>/g, ''); }
function stripControl(str)      { return str.replace(/[\x00-\x1F\x7F]/g, ''); }
function sanitizePwd(str)       { return stripControl(stripTags(String(str))); }

function _getField(input) { return input.closest('.form-field'); }

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

// Reglas de fortaleza compartidas — cargadas desde /assets/js/password-rules.js
const RULES = window.SS_PASSWORD_RULES;

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

function validateConfirm(nueva, confirm) {
  if (!confirm)          return 'Debes confirmar la nueva contraseña.';
  if (nueva !== confirm) return 'Las contraseñas no coinciden.';
  return null;
}

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

async function relogin(email, password) {
  let csrfToken = null;
  try {
    const r = await fetch('/api/csrf-token', { credentials: 'same-origin', headers: { 'Accept': 'application/json' } });
    if (r.ok) { const d = await r.json(); csrfToken = d.csrf_token || null; }
  } catch { /* sin CSRF */ }

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

(function init() {
  const token = localStorage.getItem('ss_token') || sessionStorage.getItem('ss_token');
  if (!token) { window.location.href = '/login/'; return; }

  let jwtEmail = null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (!payload.debe_cambiar_password) {
      window.location.href = '/menu';
      return;
    }
    jwtEmail = payload.sub || null;
  } catch {
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

  renderStrengthList(strengthEl, '');

  inputNueva.addEventListener('input', function () {
    const v = sanitizePwd(this.value);
    renderStrengthList(strengthEl, v);
    const err = RULES.validate(v);
    if (err && v.length > 0) showFieldError(this, err);
    else                     clearFieldError(this);
    if (inputConfirm.value) {
      const errC = validateConfirm(v, sanitizePwd(inputConfirm.value));
      errC ? showFieldError(inputConfirm, errC) : clearFieldError(inputConfirm);
    }
  });

  inputConfirm.addEventListener('input', function () {
    const err = validateConfirm(sanitizePwd(inputNueva.value), sanitizePwd(this.value));
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearAllErrors(form);
    hideFeedback(feedbackEl);

    const actual  = sanitizePwd(inputActual.value);
    const nueva   = sanitizePwd(inputNueva.value);
    const confirm = sanitizePwd(inputConfirm.value);

    let hasErrors = false;
    if (!actual) { showFieldError(inputActual, 'La contraseña actual es obligatoria.'); hasErrors = true; }

    const errNueva = RULES.validate(nueva);
    if (errNueva) { showFieldError(inputNueva, errNueva); hasErrors = true; }

    const errConfirm = validateConfirm(nueva, confirm);
    if (errConfirm) { showFieldError(inputConfirm, errConfirm); hasErrors = true; }

    if (hasErrors) { form.querySelector('.form-field--error input')?.focus(); return; }

    const btn = document.getElementById('pwd-submit-btn');
    btn.disabled = true;
    btn.textContent = 'Guardando…';

    try {
      await submitCambio({ password_actual: actual, password_nueva: nueva, password_confirm: confirm }, token);
      const newToken = jwtEmail ? await relogin(jwtEmail, nueva) : null;
      if (newToken) {
        localStorage.setItem('ss_token', newToken);
      } else {
        localStorage.removeItem('ss_token');
        sessionStorage.removeItem('ss_token');
      }
      form.hidden = true;
      exitoEl.hidden = false;
      setTimeout(() => { window.location.href = newToken ? '/menu' : '/login'; }, 2000);
    } catch (err) {
      showFieldError(inputNueva, err.message || 'No se pudo cambiar la contraseña. Inténtalo de nuevo.');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Guardar nueva contraseña';
    }
  });
}());
