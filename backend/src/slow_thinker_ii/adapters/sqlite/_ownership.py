"""One backend owns a database: an exclusive kernel lock on `<canonical path>.owner`."""

import fcntl
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def own_store(path: Path) -> Generator[None]:
    """Holds the lock until the block ends; the kernel releases it if the process exits."""
    canonical = path.resolve()
    canonical.parent.mkdir(parents=True, exist_ok=True)
    lease = canonical.with_name(f"{canonical.name}.owner")
    with lease.open("a+b") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError("Another backend owns this store") from error
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
