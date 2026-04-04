import { Component, inject } from '@angular/core';
import { SidenavService } from '../../services/sidenav.service';

interface Tool {
  id: string;
  label: string;
}

// Placeholder hasta que existan herramientas reales
const PLACEHOLDER_TOOLS: Tool[] = [
  { id: 'tool-1', label: 'Herramienta 1' },
  { id: 'tool-2', label: 'Herramienta 2' },
  { id: 'tool-3', label: 'Herramienta 3' },
  { id: 'tool-4', label: 'Herramienta 4' },
  { id: 'tool-5', label: 'Herramienta 5' },
];

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.html',
  styleUrl: './sidenav.scss',
  standalone: true,
})
export class SidenavComponent {
  readonly sidenavService = inject(SidenavService);
  readonly tools: Tool[] = PLACEHOLDER_TOOLS;
}
