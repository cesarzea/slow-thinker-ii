# Installed components

Installs component packages offline from hash-locked wheels into isolated environments,
publishes each verified installation as a resolution, and loads the declaration that each
package ships. `InstalledComponents` gives the platform the declarations of the configured
resolutions and serves as the launch target of the component hosts.

Use the [public entry point](__init__.py); private implementation files are not an
integration API. See [specification.md](specification.md) for the interface, the behaviour
and the acceptance criteria.
