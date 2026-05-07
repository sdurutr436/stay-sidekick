# TODO: Configurar secretos de GitHub para CI/CD

El workflow `.github/workflows/ci.yml` necesita tres secretos en GitHub
para poder publicar las imágenes en Docker Hub.

## 1. Crear un Access Token en Docker Hub

1. Ir a [hub.docker.com](https://hub.docker.com) → Account Settings → Security → Access Tokens
2. Crear un token con permisos **Read & Write**
3. Copiar el token (solo se muestra una vez)

## 2. Crear los repositorios en Docker Hub

Antes de que el workflow haga el primer push, los repositorios deben existir
(Docker Hub los crea automáticamente en el primer push si la cuenta es pública,
pero mejor crearlos a mano para controlar la visibilidad):

- `<usuario>/stay-sidekick-backend`
- `<usuario>/stay-sidekick-frontend`
- `<usuario>/stay-sidekick-web`
- `<usuario>/stay-sidekick-nginx`

## 3. Añadir los secretos en GitHub

Ir a: **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

| Nombre del secreto    | Valor                                      |
|-----------------------|--------------------------------------------|
| `DOCKERHUB_USERNAME`  | Tu usuario de Docker Hub                   |
| `DOCKERHUB_TOKEN`     | El Access Token del paso 1                 |
| `TURNSTILE_SITE_KEY`  | Site Key pública de Cloudflare Turnstile   |

> `TURNSTILE_SITE_KEY` es la clave **pública** (la que va en el HTML).
> Si todavía no está configurado Turnstile, puedes dejarla vacía — la imagen se
> construirá igualmente sin el widget activo.

## 4. (Recomendado) Proteger la rama main

Para que el workflow sea el gate real antes de cualquier merge:

1. Ir a: **GitHub repo → Settings → Branches → Add branch ruleset**
2. Seleccionar la rama `main`
3. Activar **Require status checks to pass before merging**
4. Añadir los checks: `Angular build`, `11ty build`, `Python lint`

Con esto, ningún PR puede mergearse a main si alguno de los tres jobs de CI falla,
y por tanto el job `publicar` nunca correrá con código roto.
