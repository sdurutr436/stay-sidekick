import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

type IconSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'app-icon',
  templateUrl: './icon.html',
  styleUrl: './icon.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IconComponent {
  @Input() size: IconSize = 'sm';
  @Input() label = '';

  get hostClasses(): string {
    return `svg svg--${this.size}`;
  }
}
