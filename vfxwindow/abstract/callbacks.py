from __future__ import absolute_import

from collections import defaultdict
from contextlib import contextmanager
from functools import wraps
import weakref

from ..exceptions import UnknownCallbackError


class CallbackProxy(object):
    """Hold the callback data for easy registering/unregistering."""

    def __init__(self, name, register, unregister, func, args, kwargs, intercept=None):
        """Create a proxy.

        Parameters:
            name (str): Name to give to the proxy to display in messages.
            register (callable): Function to register the callback.
            unregister (callable): Function to unregister the callback.
            func (callable): Function to register.
            args: User defined for the register function.
            kwargs: User defined for the register function.
            itercept (callable): Function to determine if the callback should run.
                Returning True will intercept and stop the callback.
                It should take the same args and kwargs as `func`.
        """
        self._id = None
        self._name = name
        self._register = register
        self._unregister = unregister
        self._func = func
        self._args = args
        self._kwargs = kwargs
        self._itercept = intercept if intercept is not None else lambda *args, **kwargs: False

        self._registered = False
        self._result = None

        @wraps(func)
        def runCallback(*args, **kwargs):
            """Run the callback function."""
            if intercept is None or not intercept(*args, **kwargs):
                print('Running {}...'.format(name))
                func(*args, **kwargs)

        # Copy over custom data (eg. Blender's '_bpy_persistent' attribute)
        for k, v in vars(func).items():
            setattr(runCallback, k, v)

        self.func = runCallback

    def __bool__(self):
        return self.registered
    __nonzero__ = __bool__

    def __repr__(self):
        return '<{}({!r}, {})>'.format(type(self).__name__, self._name, self._func)

    def getUnregisterParam(self):
        """Get the parameter to pass to the unregister function.
        This may require overriding.
        """
        return self._result

    @property
    def registered(self):
        """Determine if the callback is registered."""
        return self._registered

    def register(self):
        """Register the callback."""
        if not self.registered:
            print('Registering: {}'.format(self._name))
            self._result = self._register(self.func, *self._args, **self._kwargs)
            self._registered = True
        return self

    def unregister(self):
        """Unregister the callback."""
        if self.registered:
            print('Unregistering: {}'.format(self._name))
            self._unregister(self.getUnregisterParam())
            self._registered = False
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
