import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { SidenavService } from '../../../services/sidenav.service';

interface Tool {
  id: string;
  label: string;
  route: string | null; // null = herramienta todavía sin ruta asignada
}

const TOOLS: Tool[] = [
  { id: 'maestro-apartamentos',          label: 'Maestro de apartamentos',    route: '/maestro-apartamentos'          },
  { id: 'sincronizador-contactos',       label: 'Sincronizador de contactos', route: '/sincronizador-contactos'       },
  { id: 'notificaciones-checkin-tardio', label: 'Notificaciones check-in',    route: '/notificaciones-checkin-tardio' },
  { id: 'mapa-calor',            label: 'Mapa de calor',           route: '/mapa-calor'                 },
  { id: 'vault-comunicaciones', label: 'Vault de comunicaciones', route: '/vault-comunicaciones' },
  // Hoja de estilos: herramienta interna de desarrollo, fuera de las 5 del panel
  { id: 'hoja-estilos',         label: 'Hoja de estilos',         route: '/hoja-estilos'         },
];

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.html',
  styleUrl: './sidenav.scss',
  standalone: true,
  imports: [RouterLink, RouterLinkActive],
})
export class SidenavComponent {
  readonly sidenavService = inject(SidenavService);
  readonly tools: Tool[] = TOOLS;
}
