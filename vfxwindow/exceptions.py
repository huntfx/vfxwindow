
class NotImplementedApplicationError(ImportError, NotImplementedError):
    """Basically acts as a NotImplementedError, but "except ImportError" will catch it."""


class CallbackAliasNotFoundError(KeyError):
    """Raise if the callback alias is not found."""


class CallbackAliasExistsError(KeyError):
    """Raise if the callback alias already exists."""


class VFXWinDeprecationWarning(DeprecationWarning):
    """Subclassed warning to allow finer control of messages."""
