import eslint from '@eslint/js';
import prettier from 'eslint-config-prettier';
import reactHooks from 'eslint-plugin-react-hooks';
import sonarjs from 'eslint-plugin-sonarjs';
import {defineConfig, globalIgnores} from 'eslint/config';
import tseslint from 'typescript-eslint';

export default defineConfig([
  globalIgnores(['**/node_modules/**', '**/dist/**', 'coverage/**', '.cache/**']),
  eslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    extends: [tseslint.configs.strictTypeChecked, tseslint.configs.stylisticTypeChecked],
    languageOptions: {parserOptions: {projectService: true, tsconfigRootDir: import.meta.dirname}},
    rules: {
      '@typescript-eslint/no-explicit-any': 'error',
      '@typescript-eslint/explicit-module-boundary-types': 'error',
      '@typescript-eslint/switch-exhaustiveness-check': 'error',
      '@typescript-eslint/consistent-type-imports': 'error',
      'no-restricted-syntax': [
        'error',
        {selector: 'ExportDefaultDeclaration', message: 'Use named exports.'},
      ],
    },
  },
  sonarjs.configs.recommended,
  {
    rules: {
      'max-lines': ['error', {max: 150, skipBlankLines: false, skipComments: false}],
      'max-lines-per-function': [
        'error',
        {max: 30, skipBlankLines: false, skipComments: false, IIFEs: true},
      ],
      complexity: ['error', 8],
      'sonarjs/cognitive-complexity': ['error', 10],
      eqeqeq: ['error', 'always'],
    },
  },
  {files: ['frontend/src/**/*.{ts,tsx}'], extends: [reactHooks.configs.flat['recommended-latest']]},
  {files: ['**/*.config.ts'], rules: {'no-restricted-syntax': 'off'}},
  {
    files: ['**/*.cjs'],
    languageOptions: {sourceType: 'commonjs', globals: {module: 'writable', require: 'readonly'}},
  },
  prettier,
]);
