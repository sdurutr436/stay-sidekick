---
id: componentes-standalone
title: Componentes standalone
sidebar_position: 3
description: Cómo se organizan átomos, moléculas y organismos BEM en la SPA.
---

# Componentes standalone

Todos los componentes de la SPA son **standalone** (no hay `NgModule`). Cada uno declara sus propios `imports` en el decorador `@Component`. Esto simplifica el árbol de dependencias y favorece el `tree-shaking` en el build de producción.

## Pirámide BEM

Los componentes se reparten en tres carpetas que se corresponden con los niveles del **Atomic Design**, pero usando vocabulario BEM/SCSS para el estilo:

| Carpeta | Rol | Ejemplos |
|---------|-----|----------|
| `components/atoms/` | Bloques mínimos sin lógica de negocio | `button`, `badge`, `icon`, `logo`, `tipografia` |
| `components/molecules/` | Composición de átomos con un único propósito | `dropdown-buscador`, `card-herramienta`, `input-field` |
| `components/organisms/` | Bloques completos del layout | `header`, `footer`, `sidenav`, `modal`, `heatmap-grid` |

Los estilos del propio `.component.scss` se mantienen **vacíos a propósito**. Toda la apariencia vive en el SCSS compartido (`frontend/src/styles/components/_<bloque>.scss`) y se sirve global. Esto permite que el sitio 11ty pinte exactamente los mismos componentes sin duplicar código.

## Plantilla de componente

```ts
import { ChangeDetectionStrategy, Component, input, output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card-herramienta',
  standalone: true,
  imports: [CommonModule],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './card-herramienta.html',
  styleUrls: ['./card-herramienta.scss'],
})
export class CardHerramientaComponent {
  /** Slug de la herramienta — se usa como key en la lista de tarjetas. */
  readonly slug = input.required<string>();

  /** Estado de la conexión externa (PMS, Google, etc.). */
  readonly conexion = input<'ok' | 'pendiente' | 'error'>('pendiente');

  /** Click sobre la tarjeta (cuando está habilitada). */
  readonly abierta = output<string>();
}
```

Convenciones aplicadas:

- `selector` con prefijo `app-`.
- `ChangeDetectionStrategy.OnPush` por defecto — menos ciclos y obliga a inputs inmutables.
- Inputs reactivos con `input()` (firmas/signals de Angular 17+).
- Outputs con `output()` en lugar de `EventEmitter`.
- JSDoc en cada `input`/`output` — TypeDoc lo recoge y lo publica en el sidebar de la API.

## Naming BEM

El bloque CSS usa el mismo nombre que el componente (`card-herramienta`). Los modificadores siguen el patrón BEM: `card-herramienta--deshabilitada`, `card-herramienta__icono`, `card-herramienta__estado--error`.

## Tests por componente

Cada componente tiene su `*.spec.ts` con al menos:

- Render básico (`fixture.detectChanges()` sin errores).
- Casos de input → DOM esperado.
- Eventos: el componente emite el output cuando corresponde.

El umbral mínimo del 90 % de cobertura aplica también a los componentes; los `.html` están excluidos por el `coverageExclude` de `angular.json`.
