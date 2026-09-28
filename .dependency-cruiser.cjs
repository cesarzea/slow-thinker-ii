module.exports = {
  forbidden: [
    {name: 'no-cycles', severity: 'error', from: {}, to: {circular: true}},
    {
      name: 'feature-public-entries',
      severity: 'error',
      from: {path: '^frontend/src/features/([^/]+)/'},
      to: {path: '^frontend/src/features/', pathNot: '^frontend/src/features/$1/'},
    },
    {
      name: 'public-entries-only',
      severity: 'error',
      from: {path: '^frontend/src/', pathNot: '^frontend/src/features/'},
      to: {path: '^frontend/src/features/', pathNot: '/index[.]tsx?$'},
    },
    {
      name: 'no-dev-in-production',
      severity: 'error',
      from: {path: '^frontend/src/'},
      to: {dependencyTypes: ['npm-dev']},
    },
    {
      name: 'no-tests-in-production',
      severity: 'error',
      from: {path: '^frontend/src/'},
      to: {path: '/tests/'},
    },
    {
      name: 'no-undeclared-dependencies',
      severity: 'error',
      from: {},
      to: {dependencyTypes: ['npm-no-pkg', 'npm-unknown']},
    },
    {name: 'no-unresolved-imports', severity: 'error', from: {}, to: {couldNotResolve: true}},
  ],
  options: {
    doNotFollow: {path: 'node_modules'},
    tsPreCompilationDeps: true,
    combinedDependencies: true,
    tsConfig: {fileName: 'tsconfig.json'},
    enhancedResolveOptions: {exportsFields: ['exports'], conditionNames: ['import', 'default']},
  },
};
