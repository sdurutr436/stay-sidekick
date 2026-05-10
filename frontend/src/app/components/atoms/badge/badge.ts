import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

type BadgeVariant = 'default' | 'outline' | 'solid';

@Component({
  selector: 'app-badge',
  templateUrl: './badge.html',
  styleUrl: './badge.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BadgeComponent {
  @Input() variant: BadgeVariant = 'default';
  @Input() dot = false;

  get hostClasses(): string {
    return `badge badge--${this.variant}`;
  }
}
