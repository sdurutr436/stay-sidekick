import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-panel-seccion',
  templateUrl: './panel-seccion.html',
  styleUrl: './panel-seccion.scss',
  standalone: true,
})
export class PanelSeccionComponent {
  @Input() title = '';
  @Input() description = '';
  @Input() divider = false;
  @Input() hasIcon = false;
}
