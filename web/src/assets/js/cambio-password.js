'use strict';

function stripTags(str)         { return String(str).replace(/<[^>]*>/g, ''); }
function stripControl(str)      { return str.replace(/[\x00-\x1F\x7F]/g, ''); }
function sanitizePwd(str)       { return stripControl(stripTags(String(str))).slice(0, 128); }

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

function validatePwd(val) {
  if (!val)           return 'La contraseña es obligatoria.';
  if (val.length < 8) return 'La contraseña debe tener al menos 8 caracteres.';
  return null;
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
    throw new Error((body.errors && body.errors[0]) || `Error ${res.status}`);
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
  if (!token) { window.location.href = '/login'; return; }

  let jwtEmail = null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    if (!payload.debe_cambiar_password) {
      window.location.href = '/menu';
      return;
    }
    jwtEmail = payload.sub || null;
  } catch {
    window.location.href = '/login';
    return;
  }

  const form = document.getElementById('form-cambio-pwd');
  if (!form) return;

  const inputActual  = form.querySelector('#pwd-actual');
  const inputNueva   = form.querySelector('#pwd-nueva');
  const inputConfirm = form.querySelector('#pwd-confirm');
  const feedbackEl   = document.getElementById('pwd-feedback');
  const exitoEl      = document.getElementById('pwd-exito');

  inputNueva.addEventListener('blur', function () {
    const err = validatePwd(sanitizePwd(this.value));
    err ? showFieldError(this, err) : clearFieldError(this);
  });

  inputConfirm.addEventListener('blur', function () {
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

    const errNueva = validatePwd(nueva);
    if (errNueva) { showFieldError(inputNueva, errNueva); hasErrors = true; }

    const errConfirm = validateConfirm(nueva, confirm);
    if (errConfirm) { showFieldError(inputConfirm, errConfirm); hasErrors = true; }

    if (hasErrors) { form.querySelector('.form-field--error input')?.focus(); return; }

    const btn = document.getElementById('pwd-submit-btn');
    btn.disabled = true;
    btn.textContent = 'Guardando…';

    try {
      await submitCambio({ password_actual: actual, password_nueva: nueva }, token);
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
      showFeedback(feedbackEl, err.message || 'No se pudo cambiar la contraseña. Inténtalo de nuevo.');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Guardar nueva contraseña';
    }
  });
}());
