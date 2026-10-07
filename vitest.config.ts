import {defineConfig, mergeConfig} from 'vitest/config';
import frontend from './frontend/vite.config.ts';

export default mergeConfig(
  frontend,
  defineConfig({
    test: {
      environment: 'jsdom',
      include: ['frontend/tests/**/*.test.{ts,tsx}'],
      // obstacle-router ships extensionless ES imports that only a bundler resolves.
      server: {deps: {inline: ['obstacle-router']}},
      coverage: {
        provider: 'v8',
        reportsDirectory: 'coverage/typescript',
        include: ['frontend/src/**/*.{ts,tsx}'],
        thresholds: {lines: 90, branches: 90, functions: 90, statements: 90},
      },
    },
  }),
);
