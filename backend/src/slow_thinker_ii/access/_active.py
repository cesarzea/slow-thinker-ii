"""Private active-call index stores credential digests and revokes complete subtrees."""

import hashlib
import secrets

from ._values import AccessDenied, CallContext, InvocationLease


class ActiveCalls:
    def __init__(self) -> None:
        self.contexts: dict[str, CallContext] = {}
        self._tokens: dict[bytes, str] = {}
        self._digests: dict[str, bytes] = {}
        self._executing: dict[str, str] = {}

    def issue(self, context: CallContext) -> InvocationLease:
        token = secrets.token_urlsafe(32)
        digest = hashlib.sha256(token.encode()).digest()
        self.contexts[context.call_id] = context
        self._executing[context.call_id] = context.target.instance
        self._tokens[digest] = context.call_id
        self._digests[context.call_id] = digest
        return InvocationLease(context, token)

    def authenticate(self, token: str, now: float) -> CallContext:
        digest = hashlib.sha256(token.encode()).digest()
        identity = self._tokens.get(digest)
        context = self.contexts.get(identity) if identity is not None else None
        if context is None or context.deadline <= now:
            raise AccessDenied("invalid_authority")
        return context

    def busy(self, instance: str) -> bool:
        return instance in self._executing.values()

    def release(self, call_id: str) -> None:
        self._executing.pop(call_id, None)

    def executing(self) -> tuple[str, ...]:
        return tuple(self._executing)

    def subtree(self, call_id: str) -> tuple[str, ...]:
        found = [call_id] if call_id in self.contexts else []
        for parent in found:
            found.extend(
                item.call_id for item in self.contexts.values() if item.parent_call_id == parent
            )
        return tuple(found)

    def revoke(self, identities: tuple[str, ...]) -> None:
        for identity in identities:
            self.contexts.pop(identity)
            self._tokens.pop(self._digests.pop(identity))
