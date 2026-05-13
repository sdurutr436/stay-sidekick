# Problema: add_header en nginx rompe los estilos de Angular

**Detectado:** 2026-05-13  
**Afecta a:** `nginx/nginx.conf` (entorno Docker local)  
**Estado:** resuelto — los headers de seguridad solo se aplican en Railway (`nginx.railway.conf`)

---

## Síntoma

Al añadir headers de seguridad HTTP (`X-Frame-Options`, `X-Content-Type-Options`,
`Referrer-Policy`, `Content-Security-Policy`) al proxy nginx de docker-compose,
los estilos CSS de la aplicación Angular dejan de cargarse al navegar entre rutas.

El fallo es intermitente: la primera carga puede parecer funcionar brevemente,
pero cualquier navegación posterior muestra la app sin estilos.

---

## Causa raíz

El proxy nginx enruta el tráfico entre tres upstreams distintos:

```
/api/*   → backend  (Flask)
/menu/*  → frontend (Angular SPA, nginx interno)
/*       → web      (11ty estático, nginx interno)
```

La directiva `add_header` en nginx tiene una regla de herencia no obvia:
**si un bloque `location` tiene sus propios `add_header`, NO hereda los del
bloque `server` padre**. El efecto práctico es que headers definidos en el
server block no llegan a locations que tengan add_header propio.

Sin embargo, el problema real no era de herencia sino de **incompatibilidad
entre los headers añadidos y el ciclo de carga de assets de Angular**:

- Angular compila con `--base-href=/menu/`, por lo que sus assets
  (`styles.HASH.css`, `main.HASH.js`, chunks lazy) se solicitan bajo `/menu/*`.
- Esas peticiones pasan por `location /menu`, que aplica un rewrite
  (`^/menu/?(.*)$ /$1 break`) antes de hacer proxy al upstream del frontend.
- Cualquier `add_header` activo durante ese ciclo — ya sea en el server block
  o heredado — interfiere con la respuesta de los assets estáticos servidos
  por el nginx interno del contenedor Angular.

Se investigaron múltiples variantes (CSP solo en `location /`, headers solo en
server block, headers solo en location /, sin CSP) y todas producían el fallo.
La única configuración que no rompe Angular es **no añadir `add_header`
en el nginx proxy del entorno docker-compose local**.

---

## Por qué el entorno Railway no tiene este problema

`nginx.railway.conf` aplica el CSP exclusivamente dentro de `location /`
(el upstream de 11ty). En Railway, el routing es idéntico al local pero
la configuración de headers lleva funcionando desde antes de este incidente.

La diferencia clave: en Railway, el CSP preexistía en `location /` antes de
añadir los otros tres headers. En el conf local, todos los headers se añadieron
a la vez y sobre un bloque que previamente no tenía ninguno, lo que puede
haber afectado al comportamiento del proxy con `proxy_intercept_errors on`.

---

## Solución aplicada

`nginx/nginx.conf` (docker-compose local): **sin ningún `add_header`**.
Los headers de seguridad se evidencian a través de `nginx/nginx.railway.conf`.

```nginx
# nginx.conf local — sin add_header
location / {
    proxy_intercept_errors on;
    proxy_pass         http://web_upstream;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
}
```

```nginx
# nginx.railway.conf — CSP solo en location / (11ty)
location / {
    ...
    add_header Content-Security-Policy "..." always;
}
```

---

## Lección aprendida

En un proxy nginx multi-upstream con `rewrite + proxy_pass`, añadir `add_header`
puede afectar al ciclo de resolución de assets de frameworks SPA como Angular,
especialmente cuando:

- El SPA usa un `base-href` no raíz (ej. `/menu/`)
- El proxy hace rewrite del prefijo antes del `proxy_pass`
- El upstream del SPA tiene su propio nginx con `try_files`

La práctica segura es añadir headers de seguridad HTTP directamente en el
**nginx interno de cada upstream** (el que sirve los ficheros estáticos),
no en el proxy inverso que distribuye el tráfico entre upstreams.
