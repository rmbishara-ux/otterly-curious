class Pending(Exception):
    """The request was queued for a human/agent to fulfil; re-run the stage later."""


class Unavailable(Exception):
    """The provider cannot do this (e.g. no video model); the stage should use its fallback."""


class Adapter:
    name = "base"
    unit = "credits"

    def __init__(self, ep):
        self.ep = ep

    def generate(self, req, out):
        """Write the result to `out` and return the cost. Raise Pending or Unavailable when appropriate."""
        raise NotImplementedError
