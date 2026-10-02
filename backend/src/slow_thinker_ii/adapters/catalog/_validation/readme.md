# Static definition validation

Private implementation package for `GraphDefinitionValidator`. It groups local
schema resolution, safe diagnostics, component configuration, graph references
and finite/conditional binding rules. Cross-package consumers use the parent
catalog's public validator; these helper interfaces are not integration APIs.

See [specification.md](specification.md) and the
[parent specification](../specification.md) for responsibility and verification.
