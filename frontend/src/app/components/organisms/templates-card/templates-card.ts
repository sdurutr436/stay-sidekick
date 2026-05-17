import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
  selector: 'app-templates-card',
  templateUrl: './templates-card.html',
  styleUrl: './templates-card.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TemplatesCardComponent {
  @Input() title = 'Plantillas';
  @Input() emptyMessage = 'No hay plantillas guardadas.';
  @Input() total: number | null = null;
  @Input() isEmpty = false;
}
