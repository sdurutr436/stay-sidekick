import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { NgIconComponent } from '@ng-icons/core';
import { SidenavService } from '../../../services/sidenav.service';

interface Tool {
  id: string;
  label: string;
  route: string | null;
  icon: string;
}

const TOOLS: Tool[] = [
  { id: 'maestro-apartamentos',          label: 'Maestro de apartamentos',    route: '/maestro-apartamentos',          icon: 'phosphorBuildings'   },
  { id: 'sincronizador-contactos',       label: 'Sincronizador de contactos', route: '/sincronizador-contactos',       icon: 'phosphorAddressBook' },
  { id: 'notificaciones-checkin-tardio', label: 'Notificaciones check-in',    route: '/notificaciones-checkin-tardio', icon: 'phosphorBellRinging' },
  { id: 'mapa-calor',                    label: 'Mapa de calor',              route: '/mapa-calor',                    icon: 'phosphorFireSimple'  },
  { id: 'vault-comunicaciones',          label: 'Vault de comunicaciones',    route: '/vault-comunicaciones',          icon: 'phosphorChatText'    },
  // Herramienta interna de desarrollo, fuera de las 5 del panel de usuario
  { id: 'hoja-estilos',                  label: 'Hoja de estilos',            route: '/hoja-estilos',                  icon: 'phosphorSwatches'    },
];

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.html',
  styleUrl: './sidenav.scss',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, NgIconComponent],
})
export class SidenavComponent {
  readonly sidenavService = inject(SidenavService);
  readonly tools: Tool[] = TOOLS;
}
