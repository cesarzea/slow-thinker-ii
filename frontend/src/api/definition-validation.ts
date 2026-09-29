import {Ajv2020} from 'ajv/dist/2020.js';
import graphSchema from '../../../docs/contracts/schemas/graph.schema.json';

export function validDefinition(value: unknown): boolean {
  const validator = new Ajv2020({strict: false, allErrors: false});
  return validator.validate(graphSchema, value);
}
