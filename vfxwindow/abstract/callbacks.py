from __future__ import absolute_import

from collections import defaultdict
from contextlib import contextmanager
import weakref

from ..exceptions import UnknownCallbackError


class CallbackProxy(object):
    """Hold the callback data for easy registering/unregistering."""

    def __init__(self, name, register, unregister, func, args, kwargs):
        self._id = None
        self._name = name
        self._register = register
        self._unregister = unregister
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __bool__(self):
        return self.registered
    __nonzero__ = __bool__

    def __repr__(self):
        return '<{}({!r}, {})>'.format(type(self).__name__, self._name, self._func)

    @property
    def registered(self):
        """Determine if the callback is registered."""
        return self._id is not None

    def register(self):
        """Register the callback."""
        if self._id is None:
            print('Registering: {}'.format(self._name))
            self._id = self._register(self._func, *self._args, **self._kwargs)
        return self

    def unregister(self):
        """Unregister the callback."""
        if self._id is not None:
            print('Unregistering: {}'.format(self._name))
            self._unregister(self._id)
            self._id = None
        return self


class AbstractCallbacks(object):
    """Base class for callbacks."""

    def __init__(self, gui):
        self._gui = weakref.ref(gui)
        self._callbacks = []
        self._groups = defaultdict(type(self))

    def __getitem__(self, group):
        return self._groups[group]

    def __delitem__(self, group):
        self._groups[group].unregister()
        del self._groups[group]

    def __iter__(self):
        return iter(self._groups)

    def keys(self):
        return self._groups.keys()

    def values(self):
        return self._groups.values()

    def items(self):
        return self._groups.items()

    def add(self, name, func, *args, **kwargs):
        """Add a callback."""
        return None

    def remove(self, callbackProxy):
        """Remove a callback."""
        callbackProxy.unregister()
        self._callbacks.remove(callbackProxy)

    def register(self):
        """Register all callbacks.
        This is not needed unless `unregister()` has been called.
        """
        for callback in self._callbacks:
            callback.register()

        for group in self._groups.values():
            group.register()

    def unregister(self):
        """Unregister all callbacks."""
        for callback in self._callbacks:
            callback.unregister()

        for group in self._groups.values():
            group.unregister()

    @contextmanager
    def pause(self):
        """Temporarily pause all callbacks."""
        self.unregister()
        try:
            yield
        finally:
            self.register()

    @property
    def gui(self):
        """Get the GUI the class belongs to.
        It may return None if the GUI is deleted.
        """
        return self._gui()
