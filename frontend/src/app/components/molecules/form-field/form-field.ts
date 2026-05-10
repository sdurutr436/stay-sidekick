import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { FormLabelComponent } from '../../atoms/form-label/form-label';

@Component({
  selector: 'app-form-field',
  templateUrl: './form-field.html',
  styleUrl: './form-field.scss',
  standalone: true,
  imports: [FormLabelComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FormFieldComponent {
  @Input() label = '';
  @Input() for = '';
  @Input() error = '';
  @Input() hasError = false;

  get fieldClasses(): string {
    return this.hasError ? 'form-field form-field--error' : 'form-field';
  }

  get errorId(): string {
    return this.for + '-error';
  }
}
