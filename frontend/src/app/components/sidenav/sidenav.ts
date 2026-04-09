import { Component, inject } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { SidenavService } from '../../services/sidenav.service';

interface Tool {
  id: string;
  label: string;
  route: string | null; // null = herramienta todavía sin ruta asignada
}

const TOOLS: Tool[] = [
  { id: 'maestro-apartamentos', label: 'Maestro de apartamentos', route: '/menu/maestro-apartamentos' },
  { id: 'sincronizador-contactos', label: 'Sincronizador de contactos', route: '/menu/sincronizador-contactos' },
  { id: 'tool-3', label: 'Herramienta 3', route: null },
  { id: 'tool-4', label: 'Herramienta 4', route: null },
  { id: 'tool-5', label: 'Herramienta 5', route: null },
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
