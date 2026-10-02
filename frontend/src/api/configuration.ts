import {DefinitionTransport} from './definition-transport.ts';
import {DefinitionError} from './definition-errors.ts';
import {
  configurationCatalogSchema,
  configurationReceiptSchema,
  limitsCommandSchema,
} from './configuration-schemas.ts';
import type {ConfigurationCatalog, ConfigurationReceipt} from './configuration-schemas.ts';

export class ConfigurationClient extends DefinitionTransport {
  async catalog(signal: AbortSignal): Promise<ConfigurationCatalog> {
    return await this.read('/configuration/catalog', configurationCatalogSchema, signal);
  }

  async limits(body: string, signal: AbortSignal): Promise<ConfigurationReceipt> {
    const command = limitsCommandSchema.safeParse(commandValue(body));
    if (!command.success) throw new DefinitionError('invalid_limits');
    try {
      return await this.read(
        '/configuration/limits',
        configurationReceiptSchema,
        signal,
        body,
        (reply) => reply.command_id === command.data.command_id,
      );
    } catch (error) {
      if (
        error instanceof DefinitionError &&
        !['operator_service_unavailable', 'response_too_large'].includes(error.code)
      )
        throw error;
      throw new Error(
        'Configuration update unconfirmed. Replay the unchanged command to recover.',
        {cause: error},
      );
    }
  }
}

function commandValue(body: string): unknown {
  try {
    return JSON.parse(body) as unknown;
  } catch {
    throw new DefinitionError('invalid_limits');
  }
}
