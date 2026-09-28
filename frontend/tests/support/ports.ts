import {once} from 'node:events';
import {createServer} from 'node:net';

async function availablePort(): Promise<number> {
  const server = createServer();
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const address = server.address();
  await new Promise<void>((resolve, reject) => {
    server.close((error) => {
      if (error) reject(error);
      else resolve();
    });
  });
  if (address === null || typeof address === 'string') throw new Error('Missing test port');
  return address.port;
}

export async function testPort(name: string): Promise<string> {
  const configured = process.env[name];
  const port = configured === undefined ? await availablePort() : Number(configured);
  if (!Number.isSafeInteger(port) || port < 1 || port > 65535) throw new Error('Invalid test port');
  process.env[name] = String(port);
  return String(port);
}
