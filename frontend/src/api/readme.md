# api

Validated access to the [operator API](../../../docs/contracts/operator-api.md) for the
browser interface: a transport with bounded replies that sends the bearer credential,
or none on a server without operator authentication, the
`OperatorClient`, zod schemas for every reply and the `ApiError` raised for every
failure. See the [specification](specification.md).
