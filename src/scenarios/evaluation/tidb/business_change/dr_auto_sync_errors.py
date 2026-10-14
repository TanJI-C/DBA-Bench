"""Structured DR endpoint read failures shared by runtime and evaluation."""

class K09FinalStateUnavailable(RuntimeError):
    """A trusted K09 endpoint returned a structured final-state read error."""

    def __init__(self, context: str, response: object):
        self.context = context
        self.response = response
        super().__init__(f"{context} final state is unavailable: response={response!r}")
