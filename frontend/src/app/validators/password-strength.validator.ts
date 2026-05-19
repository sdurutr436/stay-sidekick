import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

/**
 * Reglas de fortaleza para contraseñas nuevas — fuente de verdad única
 * en el frontend Angular. Reflejado en:
 *   - backend/app/auth/password_rules.py
 *   - web/src/assets/js/password-rules.js
 *
 * El máximo de 20 caracteres es SECRETO: no debe exponerse en la lista
 * pública de criterios — solo aparece como error cuando se supera.
 */
export const PASSWORD_MIN_LENGTH = 8;
export const PASSWORD_MAX_LENGTH = 20;
export const PASSWORD_SPECIAL_CHARS = '!@#$%^&*-_=+.,;:?';

export const PASSWORD_RULES = [
  { id: 'minLength', label: `Mínimo ${PASSWORD_MIN_LENGTH} caracteres`,                            test: (v: string) => v.length >= PASSWORD_MIN_LENGTH },
  { id: 'upper',     label: 'Al menos 1 letra mayúscula',                                          test: (v: string) => /[A-Z]/.test(v) },
  { id: 'lower',     label: 'Al menos 1 letra minúscula',                                          test: (v: string) => /[a-z]/.test(v) },
  { id: 'digit',     label: 'Al menos 1 número',                                                   test: (v: string) => /\d/.test(v) },
  { id: 'special',   label: `Al menos 1 carácter especial (${PASSWORD_SPECIAL_CHARS})`,            test: (v: string) => /[!@#$%^&*\-_=+.,;:?]/.test(v) },
] as const;

export type PasswordCriterionId = typeof PASSWORD_RULES[number]['id'] | 'maxLength';

export class PasswordStrengthValidator {
  /**
   * Valida que el valor cumpla todas las reglas de fortaleza.
   * Devuelve un mapa de errores compatible con Reactive Forms o `null`.
   */
  static validate(): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const value = String(control.value ?? '');
      if (!value) return null;

      const errors: ValidationErrors = {};
      for (const rule of PASSWORD_RULES) {
        if (!rule.test(value)) errors[rule.id] = true;
      }
      if (value.length > PASSWORD_MAX_LENGTH) errors['maxLength'] = true;

      return Object.keys(errors).length ? { passwordStrength: errors } : null;
    };
  }

  /**
   * Mensaje legible para el primer error encontrado (orden de PASSWORD_RULES).
   */
  static firstMessage(errors: ValidationErrors | null | undefined): string | null {
    if (!errors) return null;
    const inner = errors['passwordStrength'] as Record<string, boolean> | undefined;
    if (!inner) return null;
    if (inner['maxLength']) return `La contraseña no puede superar los ${PASSWORD_MAX_LENGTH} caracteres.`;
    if (inner['minLength']) return `La contraseña debe tener al menos ${PASSWORD_MIN_LENGTH} caracteres.`;
    if (inner['upper'])     return 'La contraseña debe contener al menos una letra mayúscula.';
    if (inner['lower'])     return 'La contraseña debe contener al menos una letra minúscula.';
    if (inner['digit'])     return 'La contraseña debe contener al menos un número.';
    if (inner['special'])   return 'La contraseña debe contener al menos un carácter especial.';
    return null;
  }

  /**
   * Validador cruzado para confirmar contraseña.
   * Aplica al control "confirm"; recibe el nombre del control "nueva" del padre.
   */
  static mustMatch(targetName: string): ValidatorFn {
    return (control: AbstractControl): ValidationErrors | null => {
      const target = control.parent?.get(targetName);
      if (!target) return null;
      const a = String(control.value ?? '');
      const b = String(target.value ?? '');
      if (!a) return null;
      return a === b ? null : { mustMatch: true };
    };
  }
}
