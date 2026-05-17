import { Component } from '@angular/core';

interface ColorToken {
  name: string;
  variable: string;
  description: string;
}

interface ColorGroup {
  label: string;
  description: string;
  tokens: ColorToken[];
}

@Component({
  selector: 'app-ds-colores',
  templateUrl: './colores.html',
  standalone: true,
})
export class DsColoresComponent {
  readonly groups: ColorGroup[] = [
    {
      label: 'Superficies',
      description: 'Fondos de página, tarjetas y popovers. Reactivos al toggle de tema.',
      tokens: [
        { name: 'background',           variable: '--background',           description: 'Fondo base de la página' },
        { name: 'card',                 variable: '--card',                 description: 'Fondo de tarjetas y paneles destacados' },
        { name: 'popover',              variable: '--popover',              description: 'Fondo de menús flotantes y popovers' },
        { name: 'muted',                variable: '--muted',                description: 'Fondo desaturado para estados vacíos o disabled' },
        { name: 'sidebar',              variable: '--sidebar',              description: 'Fondo del sidenav lateral' },
      ],
    },
    {
      label: 'Texto',
      description: 'Tinta de texto sobre superficies. Pareja con su token de superficie.',
      tokens: [
        { name: 'foreground',           variable: '--foreground',           description: 'Color principal del texto' },
        { name: 'card-foreground',      variable: '--card-foreground',      description: 'Texto sobre tarjetas' },
        { name: 'muted-foreground',     variable: '--muted-foreground',     description: 'Texto secundario o de bajo énfasis' },
        { name: 'primary-foreground',   variable: '--primary-foreground',   description: 'Texto sobre fondos primarios' },
        { name: 'secondary-foreground', variable: '--secondary-foreground', description: 'Texto sobre fondos secundarios' },
      ],
    },
    {
      label: 'Acción primaria',
      description: 'Color de marca y CTAs principales. La variante hover/active se atenúa al pulsar.',
      tokens: [
        { name: 'primary',              variable: '--primary',              description: 'CTA principal y botones llamada a la acción' },
        { name: 'btn-primary-bg',       variable: '--btn-primary-bg',       description: 'Fondo del botón primario en reposo' },
        { name: 'btn-primary-bg-hover', variable: '--btn-primary-bg-hover', description: 'Fondo del botón primario al pasar el cursor' },
        { name: 'btn-primary-bg-active',variable: '--btn-primary-bg-active',description: 'Fondo del botón primario al pulsar' },
      ],
    },
    {
      label: 'Acción secundaria',
      description: 'Acciones secundarias y de soporte. Borde marcado, fondo claro.',
      tokens: [
        { name: 'secondary',                variable: '--secondary',                description: 'Color secundario / superficies alternativas' },
        { name: 'btn-secondary-bg',         variable: '--btn-secondary-bg',         description: 'Fondo del botón secundario' },
        { name: 'btn-secondary-bg-hover',   variable: '--btn-secondary-bg-hover',   description: 'Fondo del botón secundario al pasar el cursor' },
        { name: 'btn-secondary-border',     variable: '--btn-secondary-border',     description: 'Borde del botón secundario' },
        { name: 'btn-ghost-bg-hover',       variable: '--btn-ghost-bg-hover',       description: 'Fondo al pasar el cursor sobre botones fantasma' },
      ],
    },
    {
      label: 'Acento',
      description: 'Color cálido para destacar elementos puntuales sin saturar la jerarquía.',
      tokens: [
        { name: 'accent',            variable: '--accent',            description: 'Color de acento (ámbar cálido)' },
        { name: 'accent-foreground', variable: '--accent-foreground', description: 'Texto sobre fondos de acento' },
      ],
    },
    {
      label: 'Bordes y foco',
      description: 'Líneas divisorias, contornos de inputs y anillo de foco accesible.',
      tokens: [
        { name: 'border',        variable: '--border',        description: 'Borde estándar de tarjetas e inputs' },
        { name: 'border-strong', variable: '--border-strong', description: 'Borde reforzado para estados de foco' },
        { name: 'input',         variable: '--input',         description: 'Fondo de inputs de formulario' },
        { name: 'ring',          variable: '--ring',          description: 'Anillo de foco accesible (WCAG 2.4.7)' },
      ],
    },
    {
      label: 'Destructivo',
      description: 'Acciones irreversibles (eliminar, descartar). Mismo significado en ambos temas.',
      tokens: [
        { name: 'destructive',            variable: '--destructive',            description: 'Color destructivo principal' },
        { name: 'destructive-foreground', variable: '--destructive-foreground', description: 'Texto sobre fondos destructivos' },
        { name: 'btn-danger-bg',          variable: '--btn-danger-bg',          description: 'Fondo del botón de acción destructiva' },
        { name: 'btn-danger-text',        variable: '--btn-danger-text',        description: 'Texto sobre el botón de acción destructiva' },
      ],
    },
  ];
}
