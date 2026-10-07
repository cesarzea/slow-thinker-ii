import react from '@vitejs/plugin-react';
import {defineConfig} from 'vite';

// Libraries in chunks of their own: each stays below the bundler's size warning and is
// cached across interface releases.
const LIBRARIES = [
  {name: 'react', test: /node_modules[\\/](react|react-dom|scheduler)[\\/]/},
  {name: 'flow', test: /node_modules[\\/](@xyflow|d3-[a-z]+|zustand|classcat)[\\/]/},
  {
    name: 'validation',
    test: /node_modules[\\/](ajv|zod|fast-deep-equal|fast-uri|json-schema-traverse)[\\/]/,
  },
];

export default defineConfig({
  plugins: [react()],
  build: {rolldownOptions: {output: {codeSplitting: {groups: LIBRARIES}}}},
  server: {
    host: '127.0.0.1',
    proxy: {
      // The backend accepts only its own host; the browser's origin is still checked.
      '/api': {
        target: process.env['SLOW_THINKER_API_URL'] ?? 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
});
