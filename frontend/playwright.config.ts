import {defineConfig} from '@playwright/test';
import {resolve} from 'node:path';
import {testPort} from './tests/support/ports.ts';

const root = resolve(import.meta.dirname, '..');
const [apiPort, browserPort] = await Promise.all([
  testPort('SLOW_THINKER_TEST_API_PORT'),
  testPort('SLOW_THINKER_TEST_BROWSER_PORT'),
]);
const apiUrl = `http://127.0.0.1:${apiPort}`;
const browserUrl = `http://127.0.0.1:${browserPort}`;
export default defineConfig({
  testDir: './tests/journeys',
  workers: 1,
  use: {baseURL: browserUrl, browserName: 'chromium'},
  webServer: [
    {
      command: `uv run --locked uvicorn support.offline_app:create_app --app-dir backend/tests --factory --host 127.0.0.1 --port ${apiPort}`,
      cwd: root,
      env: {SLOW_THINKER_TEST_API_ORIGIN: apiUrl, SLOW_THINKER_TEST_BROWSER_ORIGIN: browserUrl},
      url: `${apiUrl}/api/v1/graphs`,
      reuseExistingServer: false,
    },
    {
      command: `npm run dev --workspace frontend -- --port ${browserPort} --strictPort`,
      cwd: root,
      env: {SLOW_THINKER_API_URL: apiUrl},
      url: browserUrl,
      reuseExistingServer: false,
    },
  ],
});
