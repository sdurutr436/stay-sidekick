---
id: arquitectura
title: Arquitectura
sidebar_position: 2
description: Capas de la SPA, providers raíz, lazy loading y separación de responsabilidades.
---

# Arquitectura de la SPA

La SPA sigue el patrón **standalone** que Angular 17+ promueve como modo principal: no hay `NgModule`. Cada componente, guard y validador es independiente y declara sus dependencias en su propio `imports`. Los servicios singleton se proveen en `providedIn: 'root'`.

## Bootstrap

[`frontend/src/main.ts`](https://github.com/sdurutr436/stay-sidekick/blob/main/frontend/src/main.ts) arranca con `bootstrapApplication(App, appConfig)`. `appConfig` (en `app/app.config.ts`) registra los providers globales:

- `provideRouter(routes)` — definición de rutas con `loadComponent` para *lazy chunks*.
- `provideHttpClient(withInterceptors(...))` — HTTP con interceptores JWT y CSRF.
- `provideAnimationsAsync()` — animaciones perezosas para reducir el bundle inicial.

## Capas de carpeta

| Capa | Carpeta | Responsabilidad |
|------|---------|-----------------|
| Componentes | `app/components/{atoms,molecules,organisms}` | Vistas reutilizables sin acceso directo al HTTP |
| Páginas | `app/pages/` | Rutas perezosas — orquestan componentes y servicios |
| Servicios | `app/services/` | Acceso a la API REST y estado compartido (`signals`) |
| Guards | `app/guards/` | Protección de rutas (auth, rol) |
| Interceptores | `app/interceptors/` | Anexan `Authorization`, gestionan CSRF |
| Validadores | `app/validators/` | Funciones reutilizables para `Reactive Forms` |
| Estilos | `styles/` | SCSS compartido (ITCSS + BEM) |

## Lazy loading

Las rutas pesadas (mapa de calor, vault, gestión de usuarios…) cargan su componente con `loadComponent` para que `ng build --configuration production` emita un *chunk* por ruta. El log de build muestra los pesos resultantes (la salida típica los lista bajo "Lazy chunk files"). Esto mantiene el `initial` por debajo del presupuesto declarado en `angular.json` (warning 500 kB, error 1 MB).

## Seguridad en el cliente

- **JWT HS256** en `localStorage` (campo `access_token`). Un interceptor lo añade como `Authorization: Bearer <token>` a cada request HTTP.
- **CSRF *double-submit cookie*** — el backend envía `X-CSRF-Token` y el interceptor lo reenvía en cualquier `POST/PUT/PATCH/DELETE`.
- **Guards de auth y rol** — protegen rutas privadas y bloquean acceso de usuarios no administradores a vistas de gestión.

## Tests

Vitest ejecuta `*.spec.ts` con el builder de Angular `@angular/build:unit-test`. El umbral mínimo de cobertura es **90 %** en sentencias, ramas, funciones y líneas, declarado en [`vitest.config.ts`](https://github.com/sdurutr436/stay-sidekick/blob/main/frontend/vitest.config.ts). El CI sube el informe `coverage/` como artefacto.
