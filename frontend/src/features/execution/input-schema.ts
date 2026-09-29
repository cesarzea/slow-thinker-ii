import {Ajv2020} from 'ajv/dist/2020.js';
import type {ValidateFunction} from 'ajv';

export const legacyInputSchema: Readonly<Record<string, unknown>> = {
  type: 'object',
  properties: {problem: {type: 'string', minLength: 1}},
  required: ['problem'],
  additionalProperties: false,
};
export interface InputValidation {
  readonly validate: ValidateFunction | null;
  readonly error: string | null;
}

export function compileInput(schema: Readonly<Record<string, unknown>>): InputValidation {
  try {
    const validator = new Ajv2020({strict: true, allErrors: true, validateFormats: true});
    return {validate: validator.compile(schema), error: null};
  } catch {
    return {
      validate: null,
      error: 'Esquema de entrada no compatible. No se puede iniciar esta definición.',
    };
  }
}

export function inputError(validation: InputValidation, value: unknown): string | null {
  if (validation.validate === null) return validation.error;
  if (objectRecord(value) === null) return 'La entrada de ejecución debe ser un objeto JSON.';
  if (validation.validate(value)) return null;
  return (
    validation.validate.errors
      ?.map((error) => `${error.instancePath || '/'}: ${error.message ?? error.keyword}`)
      .join('; ') ?? 'Entrada inválida.'
  );
}

export function objectRecord(value: unknown): Readonly<Record<string, unknown>> | null {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) return null;
  return Object.fromEntries(Object.entries(value));
}
