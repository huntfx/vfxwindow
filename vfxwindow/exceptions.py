
class NotImplementedApplicationError(ImportError, NotImplementedError):
    """Basically acts as a NotImplementedError, but "except ImportError" will catch it."""


class UnknownCallbackError(NotImplementedError):
    """Raise if the callback name is not known."""
