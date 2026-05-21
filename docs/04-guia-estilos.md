# 4. Guía de estilos y diseño de interfaz

## Índice

- [4.1. Prototipo en Figma](#41-prototipo-en-figma)
- [4.2. Guía de estilos](#42-guía-de-estilos)
  - [Paleta de colores](#paleta-de-colores)
  - [Tipografía](#tipografía)
  - [Espaciado](#espaciado)
  - [Bordes y radios](#bordes-y-radios)
  - [Sombras y elevación](#sombras-y-elevación)
  - [Breakpoints responsive](#breakpoints-responsive)
- [4.3. Wireframes y mockups de las pantallas principales](#43-wireframes-y-mockups-de-las-pantallas-principales)
- [4.4. Componentes reutilizables](#44-componentes-reutilizables)

---

## 4.1. Prototipo en Figma

El diseño de Stay Sidekick se realizó íntegramente en Figma. El fichero contiene la guía de estilos, la biblioteca de componentes y las pantallas principales:

| Recurso | Enlace |
| --- | --- |
| **Fichero principal** (guía + componentes + pantallas) | [Ver en Figma](https://www.figma.com/design/6qsTtmTkH9XwydWiHdKtGv/Dise%C3%B1o?node-id=0-1&t=PsTLXvWAzzjkZTdo-1) |

El fichero está organizado en páginas por área operativa (maestro de apartamentos, mapa de calor, notificaciones, sincronizador, vault, perfil, gestión de usuarios) y una página dedicada a la guía de estilos y la librería de componentes reutilizables.

---

## 4.2. Guía de estilos

La fuente única de verdad del sistema cromático y tipográfico está en [`frontend/src/styles/settings/`](../frontend/src/styles/settings/). Las variables SCSS semánticas apuntan a **CSS custom properties** definidas en [`_css-variables.scss`](../frontend/src/styles/settings/_css-variables.scss), de modo que el *toggle* `.dark` recolorea toda la interfaz en una sola transición.

### Paleta de colores

El sistema cromático de Stay Sidekick es **acromático** — una escala de grises de nueve pasos en HSL — con un único **color de acento ámbar cálido** para resaltar foco e interacciones puntuales. Esta decisión refuerza el carácter operativo del producto (paneles densos en información, larga exposición visual) y deja el color para semántica.

**Acento corporativo**

| Token | Valor HSL | Hex aproximado | Uso |
| --- | --- | --- | --- |
| `--accent` | `hsl(47, 64%, 87%)` | `#EFE3BC` | Fondo de elementos destacados |
| `--accent-foreground` | `hsl(14, 26%, 29%)` | `#5D423A` | Texto sobre acento |

**Escala de grises cruda** (no reactiva al tema — uso en heatmap, gradientes, brand)

| Token | Valor | Hex |
| --- | --- | --- |
| `$color-gray-50` | `hsl(0, 0%, 97.6%)` | `#F9F9F9` |
| `$color-gray-100` | `hsl(0, 0%, 94.1%)` | `#F0F0F0` |
| `$color-gray-200` | `hsl(0, 0%, 89.0%)` | `#E3E3E3` |
| `$color-gray-300` | `hsl(0, 0%, 87.1%)` | `#DEDEDE` |
| `$color-gray-400` | `hsl(0, 0%, 62.7%)` | `#A0A0A0` |
| `$color-gray-500` | `hsl(0, 0.9%, 45.1%)` | `#737373` |
| `$color-gray-600` | `hsl(0, 0%, 37.6%)` | `#606060` |
| `$color-gray-700` | `hsl(0, 0%, 31.4%)` | `#505050` |
| `$color-gray-800` | `hsl(0, 0%, 22.7%)` | `#3A3A3A` |
| `$color-gray-900` | `hsl(0, 0%, 16.9%)` | `#2B2B2B` |
| `$color-gray-950` | `hsl(0, 0%, 12.9%)` | `#212121` |

**Modo claro — tokens semánticos clave**

| Token | Hex | Rol |
| --- | --- | --- |
| `--background` | `#F9F9F9` | Fondo general |
| `--foreground` | `#3A3A3A` | Texto primario |
| `--card` | `#FFFFFF` | Superficie de tarjeta |
| `--primary` | `#606060` | Color primario (botón) |
| `--secondary` | `#DEDEDE` | Color secundario |
| `--muted` | `#E3E3E3` | Superficie atenuada |
| `--border` | `#737373` | Borde estándar |
| `--sidebar` | `#F0F0F0` | Sidebar lateral |

**Modo oscuro — overrides clave**

| Token | Hex | Rol |
| --- | --- | --- |
| `--background` | `#2B2B2B` | Fondo general |
| `--foreground` | `#DCDCDC` | Texto primario |
| `--card` | `#333333` | Superficie de tarjeta |
| `--sidebar` | `#212121` | Sidebar lateral |
| `--border` | `#4F4F4F` | Borde estándar |

**Colores semánticos de estado** (fijos en ambos temas — preservan significado)

| Token | Hex aprox. | Uso |
| --- | --- | --- |
| `$color-success-green` | `#4CAF50` | Éxito, confirmaciones |
| `$color-warning-amber` | `#F59E0B` | Aviso, atención |
| `$color-info-blue` | `#2080E0` | Información, ayuda |
| `$color-destructive` | `#C58383` | Error, acción destructiva |

**Heatmap operativo** (semántica visual del mapa de calor)

| Token | Hex | Rol |
| --- | --- | --- |
| `$heatmap-color-checkins` | `#4CAF50` | Entradas (verde) |
| `$heatmap-color-checkouts` | `#F44336` | Salidas (rojo) |

![Paleta de colores](assets/disenio/02-paleta-colores.png)

### Tipografía

Se utiliza exclusivamente la familia **Archivo** (variable font, pesos 100–900) cargada desde [`frontend/src/styles/_fonts.scss`](../frontend/src/styles/_fonts.scss). La elección busca legibilidad continuada en paneles operativos densos con un toque industrial moderno.

La escala abarca de **10 px a 64 px** y se organiza en cinco grupos: *display*, *heading* (H1–H4), *body*, *label* y *caption*. Cuatro pesos significativos — 800 (display), 700 (heading), 500 (body/label), 400 (caption) — y cinco alturas de línea adaptadas a la jerarquía del contenido.

| Grupo | Tamaños | Peso | Line-height |
| --- | --- | --- | --- |
| Display | 64 / 48 / 36 px | 800 | 1.1 |
| Heading | 36 (H1) · 32 (H2) · 24 (H3) · 20 (H4) px | 700 (H1–H3) · 500 (H4) | 1.2 |
| Body | 18 / 16 / 14 / 12 px | 500 | 1.5 |
| Label | 14 / 12 / 11 px | 500 | 1.4 |
| Caption | 12 / 11 / 10 px | 400 | 1.4 |

![Tipografía](assets/disenio/01-tipofragias.png)

### Espaciado

El sistema se basa en una **cuadrícula de 4 px**. Todos los márgenes y separaciones de la interfaz son múltiplos de esa unidad base, con una escala estándar definida en [`_variables.scss`](../frontend/src/styles/settings/_variables.scss):

| Token | rem | px |
| --- | --- | --- |
| `$space-1` | 0.25 | 4 |
| `$space-2` | 0.5 | 8 |
| `$space-3` | 0.75 | 12 |
| `$space-4` | 1 | 16 |
| `$space-5` | 1.25 | 20 |
| `$space-6` | 1.5 | 24 |
| `$space-8` | 2 | 32 |
| `$space-10` | 2.5 | 40 |
| `$space-12` | 3 | 48 |
| `$space-16` | 4 | 64 |

Las medidas más usadas (`$space-2`, `$space-4`, `$space-6`, `$space-8`) se exponen además como custom properties (`--space-2` … `--space-8`) para usos directos desde plantillas.

### Bordes y radios

Radio base **10 px** (`--radius`), con variantes derivadas:

| Token | Valor | px |
| --- | --- | --- |
| `--radius-sm` | `calc(var(--radius) - 4px)` | 6 |
| `--radius-md` | `calc(var(--radius) - 2px)` | 8 |
| `--radius-lg` | `var(--radius)` | 10 (default) |
| `--radius-xl` | `calc(var(--radius) + 4px)` | 14 |

Ancho de borde uniforme **1 px sólido** en todos los componentes (`$border-width: 1px`).

### Sombras y elevación

Sistema de **ocho niveles** de elevación (`--shadow-2xs` → `--shadow-2xl`) con desplazamiento sutil (1×4 px) y opacidad muy baja (3 %–7 %), pensado para un *look* discreto que no compita con el contenido del panel operativo. Los componentes elevados (tarjetas, modales, sidebar) se reservan a `--shadow-md` y superiores.

### Breakpoints responsive

Definidos en [`_breakpoints.scss`](../frontend/src/styles/settings/_breakpoints.scss) y consumidos mediante mixins de [`tools/_mixins.scss`](../frontend/src/styles/tools/_mixins.scss).

| Token | Mín. (px) | Uso típico |
| --- | :---: | --- |
| `xs` | 0 | Móvil estrecho |
| `sm` | 576 | Móvil ancho |
| `md` | 768 | Tablet |
| `lg` | 992 | Escritorio |
| `xl` | 1200 | Escritorio amplio (= contenedor máximo) |
| `xxl` | 1400 | Pantallas grandes |

El contenedor central se limita a **1200 px** (`$container-max-width`); el *header* mide **64 px** en escritorio y **56 px** en móvil.

---

## 4.3. Wireframes y mockups de las pantallas principales

Se diseñaron las pantallas que dan acceso a cada herramienta operativa:

1. **Landing pública** (11ty) — producto, características y captación.
2. **Login** y cambio obligatorio de contraseña.
3. **Dashboard** — catálogo de herramientas activadas por empresa.
4. **Maestro de apartamentos** — listado, alta manual, sincronización PMS e importación XLSX.
5. **Notificaciones de check-in tardío** — plantillas y reglas por empresa.
6. **Sincronizador de contactos Google** — OAuth, sincronización y exportación CSV.
7. **Mapa de calor operativo** — configuración de columnas, umbrales y vista.
8. **Vault de comunicaciones** — catálogo de plantillas, asistente IA, system prompts.
9. **Perfil de empresa e integraciones** — claves PMS/IA, columnas XLSX, preferencias.
10. **Gestión de usuarios** — alta, baja, cambio de rol y reseteo de contraseña.

**Wireframes**

![Wireframes de las pantallas principales](assets/disenio/03-wireframes.png)

**Mockups**

![Mockups de las pantallas principales](assets/disenio/04-mockups.png)

---

## 4.4. Componentes reutilizables

La biblioteca de componentes Angular se organiza en tres niveles — **átomos**, **moléculas** y **organismos** — siguiendo la arquitectura SCSS [ITCSS](https://www.xfive.co/blog/itcss-scalable-maintainable-css-architecture/) con nomenclatura [BEM](https://getbem.com/). Cada componente define sus estados (reposo, hover, activo, deshabilitado, error) y sus variantes para tema claro/oscuro mediante CSS custom properties — no hay duplicación de reglas por tema.

| Nivel | Componentes |
| --- | --- |
| **Átomos** | `button`, `badge`, `icon`, `tag`, `form-input`, `form-input-icon`, `form-select`, `form-label`, `form-textarea`, `form-checkbox` |
| **Moléculas** | `alert`, `confirm-inline`, `accordion-item`, `form-field`, `search-bar`, `dropdown-buscador`, `tarjeta-estado`, `how-it-works-button`, `theme-toggle` |
| **Organismos** | `header`, `footer`, `sidenav`, `modal`, `tabla-crud`, `heatmap-grid`, `templates-card` |

La librería de componentes está versionada en el SPA Angular bajo [`frontend/src/app/components/`](../frontend/src/app/), con tests unitarios individuales que validan *@Input*, *@Output* y estados (ver [docs/07-pruebas.md — Frontend](07-pruebas.md#723-pruebas-unitarias--frontend)).

**Componentes — Wireframe**

![Componentes en versión wireframe](assets/disenio/05-componentes-wireframes.png)

**Componentes — Mockup**

![Componentes en versión mockup final](assets/disenio/06-componentes-mockups.png)
