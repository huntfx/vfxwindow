
class NotImplementedApplicationError(ImportError, NotImplementedError):
    """Basically acts as a NotImplementedError, but "except ImportError" will catch it."""
