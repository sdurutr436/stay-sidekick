import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

type CardVariant = 'default' | 'horizontal';

@Component({
  selector: 'app-card',
  templateUrl: './card.html',
  styleUrl: './card.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CardComponent {
  @Input() variant: CardVariant = 'default';

  get hostClasses(): string {
    return this.variant === 'horizontal' ? 'card card--horizontal' : 'card';
  }
}
