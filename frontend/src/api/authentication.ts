interface AuthenticationLease {
  readonly invalidated: () => void;
}
/** A connection's credential; `null` for a server without operator authentication. */
type Credential = string | null;
const leases = new Map<Credential, AuthenticationLease>();

/** Register the connection that must be told when its credential stops being accepted. */
export function observeAuthentication(
  credential: Credential,
  onInvalidated: () => void,
): () => void {
  const lease = {invalidated: onInvalidated};
  leases.set(credential, lease);
  return () => {
    if (leases.get(credential) === lease) leases.delete(credential);
  };
}

/** Capture the lease active when a request starts, so obsolete replies cannot invalidate a newer one. */
export function captureAuthentication(credential: Credential): () => void {
  const lease = leases.get(credential);
  return () => {
    if (lease !== undefined && leases.get(credential) === lease) lease.invalidated();
  };
}
