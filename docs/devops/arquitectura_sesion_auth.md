# Arquitectura de sesión y autenticación — Stay Sidekick

Respuestas al diagnóstico de sesión/auth del proyecto. Estado a 2026-04-21.

---

## Stack y arquitectura

### ¿Qué tecnología usa el backend/frontend?

- **Backend**: Python + Flask, con PyJWT propio y bcrypt. Sin flask-login ni flask-jwt-extended.
- **Frontend post-login**: Angular SPA (standalone components, signals).
- **Frontend pre-login**: 11ty con Nunjucks (.njk), completamente estático en build.
- **Servidor**: Nginx como pieza central (reverse proxy + servidor de estáticos).

### ¿Cómo está gestionando la sesión actualmente?

JWT en `localStorage` bajo la clave `ss_token`. Sin cookies, sin sesión en servidor.

- El login vive en 11ty (`web/src/assets/js/form-login.js`): hace `POST /api/auth/login`, recibe el JWT y lo guarda en localStorage.
- `header-auth.js` (11ty) lee `ss_token`, decodifica el JWT y muta el DOM para alternar entre "Iniciar sesión" y "Perfil".
- `AuthService` (Angular) lee `ss_token` de localStorage. Expone `getToken()`, `isLoggedIn()`, `getUser()`, `logout()`.
- No hay HttpInterceptor global — cada servicio añade `Authorization: Bearer <token>` manualmente.
- No hay route guards en Angular.

### ¿Nginx actúa como reverse proxy o sirve /menu directamente?

Nginx actúa como reverse proxy en todos los casos:

- `/api/*` → Flask (backend)
- `/menu` → Angular (contenedor frontend, rewrite elimina el prefijo `/menu`)
- `/` (resto) → 11ty (contenedor web estático)

```nginx
location /menu {
    rewrite ^/menu/?(.*)$ /$1 break;
    proxy_pass $frontend_url;
}
```

Flask no interviene en ningún momento para cargar la SPA.

---

## Sobre el problema concreto

### ¿La ruta /menu es estática o renderizada por el backend?

Completamente estática desde el punto de vista de Flask. Nginx hace proxy al contenedor Angular, que sirve su `index.html`. Flask nunca recibe esa petición.

### ¿Hay middleware de autenticación en el backend para /menu?

No. `@jwt_required` solo protege las rutas `/api/*`. La ruta `/menu` no pasa por Flask, así que no hay ninguna validación de sesión en servidor antes de entregar la SPA.

### ¿Qué pasa al acceder a /menu sin sesión?

Devuelve **200** con el HTML de Angular. La SPA carga entera. La única protección visible es que `AuthService.isLoggedIn()` devuelve `false` y el header muestra "Iniciar sesión", pero no hay redirección automática al login porque no hay route guards implementados.

---

## Sobre actores y vectores

### ¿El problema es navegador, curl, o ambos?

Ambos. `curl` recibe el `index.html` de Angular con 200. Un navegador carga la SPA completa. Los datos sensibles están en las llamadas `/api/*`, que sí están protegidas por `@jwt_required`, pero la SPA en sí es pública.

### ¿Hay WebSockets o AJAX sin autenticación?

No hay WebSockets. Las peticiones AJAX hacia `/api/*` requieren token, pero se añade manualmente en cada servicio — si algún servicio lo olvida, la petición sale sin autenticar sin ningún aviso. No hay interceptor global que lo garantice.

---

## Estado actual de protección

| Aspecto | Estado |
|---|---|
| Sin sesión → /menu | 200 + SPA cargada, sin redirección |
| Rutas post-login existentes | Solo `/menu/**` |
| Protección en Nginx | Ninguna |
| Protección en Angular | Ninguna (sin route guards) |
| Protección en Flask `/api/*` | Sí (`@jwt_required`) |

---

## Notas para implementación futura

La protección más robusta requiere dos capas:

1. **Nginx**: auth subrequest o validación de cookie antes de hacer proxy a `/menu` → redirige a `/login` si no hay sesión válida.
2. **Angular**: route guard como segunda línea (`canActivate` que llame a `AuthService.isLoggedIn()`).

La capa Flask ya está cubierta para los datos (`/api/*`).

Si se migra de localStorage a cookie httpOnly, Nginx podría validar la cookie directamente sin necesidad de una subrequest al backend en cada petición a `/menu`.
