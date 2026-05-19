import {
  ChangeDetectionStrategy,
  Component,
  computed,
  DestroyRef,
  effect,
  inject,
  input,
  output,
  signal,
} from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { NgIconComponent } from '@ng-icons/core';
import { AlertComponent } from '../../../components/molecules/alert/alert';
import { ButtonComponent } from '../../../components/atoms/button/button';
import { PanelSeccionComponent } from '../../../components/organisms/panel-seccion/panel-seccion';
import { PerfilService } from '../../../services/perfil.service';
import {
  PASSWORD_MAX_LENGTH,
  PASSWORD_RULES,
  PasswordStrengthValidator,
} from '../../../validators/password-strength.validator';

interface Alerta {
  tipo: 'success' | 'error';
  mensaje: string;
}

const PASSWORD_EDAD_AVISO_DIAS = 30;

@Component({
  selector: 'app-password-section',
  templateUrl: './password-section.html',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    ReactiveFormsModule,
    NgIconComponent,
    AlertComponent,
    ButtonComponent,
    PanelSeccionComponent,
  ],
})
export class PasswordSectionComponent {
  readonly passwordChangedAt = input<string | null>(null);
  readonly passwordChanged   = output<void>();

  private readonly fb         = inject(FormBuilder);
  private readonly service    = inject(PerfilService);
  private readonly destroyRef = inject(DestroyRef);

  readonly passwordForm: FormGroup = this.fb.group({
    actual:  this.fb.nonNullable.control('', [Validators.required]),
    nueva:   this.fb.nonNullable.control('', [
      Validators.required,
      Validators.maxLength(PASSWORD_MAX_LENGTH),
      PasswordStrengthValidator.validate(),
    ]),
    confirm: this.fb.nonNullable.control('', [
      Validators.required,
      PasswordStrengthValidator.mustMatch('nueva'),
    ]),
  });

  readonly guardando      = signal(false);
  readonly alerta         = signal<Alerta | null>(null);
  readonly edadModal      = signal(false);
  readonly criterios      = PASSWORD_RULES.map(r => ({ id: r.id, label: r.label }));
  readonly nuevaValue     = signal('');
  readonly confirmValue   = signal('');
  readonly nuevaTouched   = signal(false);
  readonly confirmTouched = signal(false);

  readonly maxLength = PASSWORD_MAX_LENGTH;

  readonly criteriosEstado = computed(() =>
    this.criterios.map(c => ({
      ...c,
      ok: PASSWORD_RULES.find(r => r.id === c.id)!.test(this.nuevaValue()),
    }))
  );

  readonly excedeMax = computed(() => this.nuevaValue().length > PASSWORD_MAX_LENGTH);

  readonly nuevaError = computed(() => {
    this.nuevaValue();
    if (!this.nuevaTouched()) return null;
    const errs = this.passwordForm.get('nueva')?.errors;
    return PasswordStrengthValidator.firstMessage(errs)
      ?? (errs?.['maxlength'] ? `La contraseña no puede superar los ${PASSWORD_MAX_LENGTH} caracteres.` : null);
  });

  readonly confirmError = computed(() => {
    this.nuevaValue();
    this.confirmValue();
    if (!this.confirmTouched()) return null;
    const errs = this.passwordForm.get('confirm')?.errors;
    if (!errs) return null;
    if (errs['mustMatch']) return 'Las contraseñas no coinciden.';
    return null;
  });

  readonly diasDesdeUltimoCambio = computed(() => {
    const at = this.passwordChangedAt();
    if (!at) return null;
    return Math.floor((Date.now() - new Date(at).getTime()) / 86_400_000);
  });

  constructor() {
    this.passwordForm.get('nueva')!.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(v => {
        this.nuevaValue.set(String(v ?? ''));
        this.passwordForm.get('confirm')!.updateValueAndValidity({ emitEvent: false });
      });
    this.passwordForm.get('confirm')!.valueChanges
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(v => this.confirmValue.set(String(v ?? '')));

    effect(() => {
      const dias = this.diasDesdeUltimoCambio();
      if (dias !== null && dias >= PASSWORD_EDAD_AVISO_DIAS) this.edadModal.set(true);
    });
  }

  cerrarEdadModal(): void {
    this.edadModal.set(false);
  }

  guardar(): void {
    this.alerta.set(null);
    this.nuevaTouched.set(true);
    this.confirmTouched.set(true);

    if (this.passwordForm.invalid) {
      this.passwordForm.markAllAsTouched();
      const msg = this.nuevaError() ?? this.confirmError() ?? 'Revisa los campos de la contraseña.';
      this.alerta.set({ tipo: 'error', mensaje: msg });
      return;
    }

    const { actual, nueva, confirm } = this.passwordForm.getRawValue();
    this.guardando.set(true);
    this.service.cambiarPassword(actual, nueva, confirm).subscribe({
      next: res => {
        if (res.ok) {
          this.alerta.set({ tipo: 'success', mensaje: 'Contraseña actualizada correctamente.' });
          this.passwordForm.reset({ actual: '', nueva: '', confirm: '' });
          this.nuevaTouched.set(false);
          this.confirmTouched.set(false);
          this.edadModal.set(false);
          this.passwordChanged.emit();
        } else {
          this.alerta.set({ tipo: 'error', mensaje: res.errors?.[0] ?? 'Error al cambiar la contraseña.' });
        }
        this.guardando.set(false);
      },
      error: err => {
        const msg = err?.error?.errors?.[0] ?? 'Error al cambiar la contraseña.';
        this.alerta.set({ tipo: 'error', mensaje: msg });
        this.guardando.set(false);
      },
    });
  }
}
