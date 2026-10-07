"""Errors that use cases and port implementations raise to adapters; messages are English."""


class GraphExists(Exception):
    def __init__(self, graph_id: str) -> None:
        self.graph_id = graph_id
        super().__init__(f"A graph with the identifier “{graph_id}” already exists.")


class GraphNotFound(LookupError):
    def __init__(self, graph_id: str) -> None:
        self.graph_id = graph_id
        super().__init__(f"Graph “{graph_id}” does not exist.")


class VersionNotFound(LookupError):
    def __init__(self, graph_id: str, version: int) -> None:
        self.graph_id = graph_id
        self.version = version
        super().__init__(f"Graph “{graph_id}” has no version {version}.")


class BranchExists(Exception):
    def __init__(self, graph_id: str, name: str) -> None:
        self.graph_id = graph_id
        self.name = name
        super().__init__(f"Graph “{graph_id}” already has a branch named “{name}”.")


class BranchNotFound(LookupError):
    def __init__(self, graph_id: str, name: str) -> None:
        self.graph_id = graph_id
        self.name = name
        super().__init__(f"Graph “{graph_id}” has no branch “{name}”.")


class InvalidBranch(ValueError):
    """A branch name that breaks the naming rule, or a start that is not one version or change."""


class ChangeNotFound(LookupError):
    def __init__(self, graph_id: str, change: int) -> None:
        self.graph_id = graph_id
        self.change = change
        super().__init__(f"Graph “{graph_id}” has no change {change}.")


class RunNotFound(LookupError):
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        super().__init__(f"Run “{run_id}” does not exist.")


class TooManyRuns(Exception):
    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(f"The limit of {limit} active runs is reached; wait until a run ends.")


class InvalidGrant(PermissionError):
    def __init__(self) -> None:
        super().__init__("The grant is missing, unknown or expired.")


class InvalidReport(ValueError):
    """A report whose kind is unknown or whose content exceeds 64 KiB."""


class StartupFailed(Exception):
    """Raised by `HostLauncher.launch` when a host cannot be launched or is not ready.

    The message is the run's English detail, for example
    `Reviewer's router@1.0.0 host was not ready within 20 seconds.`
    """
