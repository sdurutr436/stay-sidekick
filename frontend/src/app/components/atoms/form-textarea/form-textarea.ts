import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-form-textarea',
  templateUrl: './form-textarea.html',
  styleUrl: './form-textarea.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FormTextareaComponent {
  @Input() id = '';
  @Input() placeholder = '';
  @Input() value = '';
  @Input() disabled = false;
  @Input() ariaLabel = '';

  @Output() valueChange = new EventEmitter<string>();

  onInput(event: Event): void {
    const target = event.target as HTMLTextAreaElement;
    this.valueChange.emit(target.value);
  }
}
