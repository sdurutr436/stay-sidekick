import { ChangeDetectionStrategy, Component, Input, signal } from '@angular/core';
import { NgIconComponent } from '@ng-icons/core';
import { ModalComponent } from '../../organisms/modal/modal';

@Component({
  selector: 'app-how-it-works-button',
  templateUrl: './how-it-works-button.html',
  styleUrl: './how-it-works-button.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [NgIconComponent, ModalComponent],
})
export class HowItWorksButtonComponent {
  @Input() label = '¿Cómo se usa?';
  @Input() modalTitle = 'Cómo se usa esta herramienta';

  readonly open = signal(false);

  abrir(): void { this.open.set(true); }
  cerrar(): void { this.open.set(false); }
}
