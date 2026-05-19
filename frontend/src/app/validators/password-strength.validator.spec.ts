import { FormBuilder, FormControl } from '@angular/forms';
import {
  PASSWORD_MAX_LENGTH,
  PASSWORD_MIN_LENGTH,
  PASSWORD_RULES,
  PasswordStrengthValidator,
} from './password-strength.validator';

describe('PasswordStrengthValidator', () => {
  const validator = PasswordStrengthValidator.validate();

  function err(value: string) {
    return validator(new FormControl(value));
  }

  it('exporta las constantes documentadas', () => {
    expect(PASSWORD_MIN_LENGTH).toBe(8);
    expect(PASSWORD_MAX_LENGTH).toBe(20);
    expect(PASSWORD_RULES.map(r => r.id)).toEqual(['minLength', 'upper', 'lower', 'digit', 'special']);
  });

  it('considera válido un valor vacío (los campos required gestionan eso aparte)', () => {
    expect(err('')).toBeNull();
  });

  it('rechaza contraseñas demasiado cortas', () => {
    const errs = err('Ab1!a') as { passwordStrength: Record<string, true> };
    expect(errs.passwordStrength['minLength']).toBe(true);
  });

  it('rechaza contraseñas sin mayúscula', () => {
    const errs = err('abcdef1!') as { passwordStrength: Record<string, true> };
    expect(errs.passwordStrength['upper']).toBe(true);
  });

  it('rechaza contraseñas sin minúscula', () => {
    const errs = err('ABCDEF1!') as { passwordStrength: Record<string, true> };
    expect(errs.passwordStrength['lower']).toBe(true);
  });

  it('rechaza contraseñas sin número', () => {
    const errs = err('AbcdefGh!') as { passwordStrength: Record<string, true> };
    expect(errs.passwordStrength['digit']).toBe(true);
  });

  it('rechaza contraseñas sin carácter especial', () => {
    const errs = err('Abcdef12') as { passwordStrength: Record<string, true> };
    expect(errs.passwordStrength['special']).toBe(true);
  });

  it('marca maxLength solo cuando se supera el límite', () => {
    expect(err('Abcdef12!')).toBeNull();
    const errs = err('A'.repeat(21) + 'b1!') as { passwordStrength: Record<string, true> };
    expect(errs.passwordStrength['maxLength']).toBe(true);
  });

  it('acepta contraseñas que cumplen todas las reglas', () => {
    expect(err('Abcdef12!')).toBeNull();
    expect(err('Pass.word1')).toBeNull();
    expect(err('Z9z9z9z9?')).toBeNull();
  });

  describe('firstMessage()', () => {
    it('prioriza maxLength sobre los demás errores', () => {
      const errs = err('A'.repeat(21)) as { passwordStrength: Record<string, true> };
      expect(PasswordStrengthValidator.firstMessage(errs)).toContain('20');
    });

    it('devuelve null si no hay errores', () => {
      expect(PasswordStrengthValidator.firstMessage(null)).toBeNull();
    });

    it('devuelve un mensaje legible para sin-especial', () => {
      const errs = err('Abcdef12') as { passwordStrength: Record<string, true> };
      expect(PasswordStrengthValidator.firstMessage(errs)).toContain('especial');
    });

    it('devuelve mensajes específicos para cada criterio incumplido', () => {
      expect(PasswordStrengthValidator.firstMessage(err('Ab1!a'))!).toContain('al menos');
      expect(PasswordStrengthValidator.firstMessage(err('abcdef1!'))!).toContain('mayúscula');
      expect(PasswordStrengthValidator.firstMessage(err('ABCDEF1!'))!).toContain('minúscula');
      expect(PasswordStrengthValidator.firstMessage(err('AbcdefGh!'))!).toContain('número');
    });

    it('devuelve null cuando passwordStrength existe pero el inner está vacío', () => {
      expect(PasswordStrengthValidator.firstMessage({ passwordStrength: {} })).toBeNull();
    });

    it('devuelve null cuando el control no tiene errores de fortaleza (otra key)', () => {
      expect(PasswordStrengthValidator.firstMessage({ required: true })).toBeNull();
    });
  });

  describe('mustMatch()', () => {
    it('marca mustMatch cuando confirm difiere de nueva', () => {
      const fb = new FormBuilder();
      const group = fb.group({
        nueva:   fb.nonNullable.control('Abcdef12!'),
        confirm: fb.nonNullable.control('Otro1234!', [PasswordStrengthValidator.mustMatch('nueva')]),
      });
      group.get('confirm')!.updateValueAndValidity();
      expect(group.get('confirm')?.errors?.['mustMatch']).toBe(true);
    });

    it('no marca mustMatch cuando ambos coinciden', () => {
      const fb = new FormBuilder();
      const group = fb.group({
        nueva:   fb.nonNullable.control('Abcdef12!'),
        confirm: fb.nonNullable.control('Abcdef12!', [PasswordStrengthValidator.mustMatch('nueva')]),
      });
      group.get('confirm')!.updateValueAndValidity();
      expect(group.get('confirm')?.errors).toBeNull();
    });

    it('devuelve null cuando el control no tiene parent (validación temprana)', () => {
      const standalone = new FormControl('foo', [PasswordStrengthValidator.mustMatch('nueva')]);
      standalone.updateValueAndValidity();
      expect(standalone.errors).toBeNull();
    });

    it('no marca mustMatch cuando confirm está vacío (lo gestiona el Required)', () => {
      const fb = new FormBuilder();
      const group = fb.group({
        nueva:   fb.nonNullable.control('Abcdef12!'),
        confirm: fb.nonNullable.control('', [PasswordStrengthValidator.mustMatch('nueva')]),
      });
      group.get('confirm')!.updateValueAndValidity();
      expect(group.get('confirm')?.errors).toBeNull();
    });
  });
});
