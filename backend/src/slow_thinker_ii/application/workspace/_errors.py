"""Fixed workspace failures safe for transport projection."""


class WorkspaceError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code
