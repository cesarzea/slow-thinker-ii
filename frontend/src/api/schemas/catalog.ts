import {z} from 'zod';
import {jsonObjectSchema, pointerSchema, portNameSchema} from './json.ts';

const plainText = (max: number): z.ZodString =>
  z
    .string()
    .min(1)
    .max(max)
    .regex(/^[^<>]*$/u);

const numberFormatSchema = z.strictObject({
  decimals: z.number().int().min(0).max(6).optional(),
  grouping: z.boolean().optional(),
  prefix: z.string().max(8).optional(),
  suffix: z.string().max(8).optional(),
});

const uiFieldSchema = z.strictObject({
  path: pointerSchema,
  control: z.enum(['text', 'multiline', 'number', 'choice', 'list', 'code', 'schema', 'service']),
  label: plainText(60),
  help: plainText(300).optional(),
  placeholder: plainText(120).optional(),
  options: z
    .array(z.strictObject({value: z.string().max(64), label: plainText(60)}))
    .min(1)
    .max(32)
    .optional(),
  language: z.enum(['python', 'json', 'text']).optional(),
  service: z.literal('llm').optional(),
  empty_label: plainText(60).optional(),
  item_label: plainText(40).optional(),
  when: z
    .strictObject({path: pointerSchema, equals: z.union([z.string(), z.number(), z.boolean()])})
    .optional(),
  label_position: z.enum(['top', 'start']).optional(),
  align: z.enum(['start', 'end', 'center']).optional(),
  width: z.enum(['xs', 'sm', 'md', 'lg', 'full']).optional(),
  format: numberFormatSchema.optional(),
});

const uiSectionSchema = z.strictObject({
  id: z.string().regex(/^[a-z][a-z0-9_-]{0,31}$/u),
  title: plainText(40),
  fields: z.array(uiFieldSchema).min(1).max(24),
  columns: z.union([z.literal(1), z.literal(2)]).optional(),
});

const componentDeclarationSchema = z.strictObject({
  format: z.literal('slow-thinker.component/1'),
  type: z.string().regex(/^[a-z][a-z0-9-]{0,63}$/u),
  version: z.string().regex(/^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)$/u),
  label: plainText(40),
  description: plainText(300),
  icon: z.enum(['trigger', 'agent', 'router', 'output', 'memory', 'component']),
  placements: z.array(z.enum(['node', 'output', 'memory'])).min(1),
  state: z.enum(['stateless', 'stateful']),
  ports: z.strictObject({
    inputs: z.array(portNameSchema),
    outputs: z.array(portNameSchema).optional(),
    outputs_from: pointerSchema.optional(),
  }),
  uses: z.array(z.strictObject({service: z.literal('llm'), pointer: pointerSchema})),
  config_schema: jsonObjectSchema,
  initial_config: jsonObjectSchema,
  ui: z.strictObject({card: z.array(pointerSchema).max(3), sections: z.array(uiSectionSchema)}),
});

const catalogComponentSchema = componentDeclarationSchema.extend({
  origin: z.enum(['platform', 'package']),
});

const llmEntrySchema = z.strictObject({
  id: z.string().regex(/^[a-z][a-z0-9-]*\/[a-z0-9][a-z0-9.-]*$/u),
  label: z.string().min(1).max(60),
  provider: z.string().min(1),
  parameters: jsonObjectSchema,
});

export const catalogSchema = z.strictObject({
  components: z.array(catalogComponentSchema),
  llms: z.array(llmEntrySchema),
});

export type UiField = z.infer<typeof uiFieldSchema>;
export type UiSection = z.infer<typeof uiSectionSchema>;
export type ComponentDeclaration = z.infer<typeof catalogComponentSchema>;
export type LlmEntry = z.infer<typeof llmEntrySchema>;
export type Catalog = z.infer<typeof catalogSchema>;
export type ComponentIcon = ComponentDeclaration['icon'];
