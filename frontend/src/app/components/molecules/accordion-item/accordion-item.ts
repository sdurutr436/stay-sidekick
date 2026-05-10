import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
  selector: 'app-accordion-item',
  templateUrl: './accordion-item.html',
  styleUrl: './accordion-item.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AccordionItemComponent {
  @Input() titulo = '';
  @Input() count = 0;
  @Input() abierto = false;
}
