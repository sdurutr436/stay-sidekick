import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

interface DsSection {
  id: string;
  label: string;
  route: string;
}

const SECTIONS: DsSection[] = [
  { id: 'tipografia', label: 'Tipografía',  route: 'tipografia'  },
  { id: 'atomos',     label: 'Átomos',      route: 'atomos'      },
  { id: 'moleculas',  label: 'Moléculas',   route: 'moleculas'   },
  { id: 'organismos', label: 'Organismos',  route: 'organismos'  },
];

@Component({
  selector: 'app-hoja-estilos-page',
  templateUrl: './hoja-estilos.html',
  styleUrl: './hoja-estilos.scss',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
})
export class HojaEstilosPageComponent {
  readonly sections: DsSection[] = SECTIONS;
}
