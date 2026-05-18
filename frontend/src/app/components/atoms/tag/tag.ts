import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

type TagVariant = 'default' | 'success' | 'warning' | 'danger';

@Component({
  selector: 'app-tag',
  templateUrl: './tag.html',
  styleUrl: './tag.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TagComponent {
  @Input() variant: TagVariant = 'default';

  get hostClasses(): string {
    return `tag tag--${this.variant}`;
  }
}
