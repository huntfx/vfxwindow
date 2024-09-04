from __future__ import absolute_import

import logging
import weakref
from collections import defaultdict
from contextlib import contextmanager
from functools import wraps

from ..exceptions import UnknownCallbackError

logger = logging.getLogger(__name__)


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
        self._args = args
        self._kwargs = kwargs

        self._registered = False
        self._result = None

        @wraps(func)
        def runCallback(*args, **kwargs):
            """Run the callback function."""
            if intercept is None or not intercept(*args, **kwargs):
                logger.debug('Running %s...', self.name)
                func(*args, **kwargs)

        # Copy over custom data (eg. Blender's '_bpy_persistent' attribute)
        for k, v in vars(func).items():
            setattr(runCallback, k, v)

        self._func = runCallback

    def __bool__(self):
        return self.registered
    __nonzero__ = __bool__

    def __repr__(self):
        return '<{}({!r}, {})>'.format(type(self).__name__, self.name, self.func)

    @property
    def name(self):
        """Get the callback name."""
        return self._name

    @property
    def func(self):
        """Get the callback function."""
        return self._func

    def forceUnregister(self):
        """Unregister the callback without any extra checks.
        This may require overriding.
        """
        self._unregister(self._result)

    @property
    def registered(self):
        """Determine if the callback is registered."""
        return self._registered

    def register(self):
        """Register the callback."""
        if not self.registered:
            logger.info('Registering: %s', self._name)
            self._result = self._register(self.func, *self._args, **self._kwargs)
            self._registered = True
        return self

    def unregister(self):
        """Unregister the callback."""
        if self.registered:
            logger.info('Unregistering: %s', self._name)
            self.forceUnregister()
            self._registered = False
        return self


class AbstractCallbacks(object):
    """Base class for callbacks."""

    def __init__(self, gui):
        if isinstance(gui, weakref.ReferenceType):
            self._gui = gui
        else:
            self._gui = weakref.ref(gui)
        self._callbacks = []
        self._groups = defaultdict(self._new)

    def _new(self):
        return type(self)(self._gui)

    def __getitem__(self, group):
        return self._groups[group]

    def __delitem__(self, group):
        self._groups[group].delete()
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
        raise UnknownCallbackError(name)

    def remove(self, callbackProxy):
        """Remove a callback."""
        self._callbacks.remove(callbackProxy.unregister())

    def register(self):
        """Register all callbacks.
        This is not needed unless `unregister()` has been called.
        """
        logger.debug('Registering callbacks...')
        callbacks = [cb.register() for cb in self._callbacks if not cb.registered]
        for group in self._groups.values():
            callbacks.extend(group.register())
        return callbacks

    def unregister(self):
        """Unregister all callbacks."""
        logger.debug('Unregistering callbacks...')
        callbacks = [cb.unregister() for cb in self._callbacks if cb.registered]
        for group in self._groups.values():
            callbacks.extend(group.unregister())
        return callbacks

    def delete(self):
        """Delete all callbacks."""
        logger.debug('Deleting callbacks...')
        callbacks = [cb.unregister() for cb in self._callbacks]
        for group in self._groups.values():
            callbacks.extend(group.delete())

        self._callbacks[:] = []
        self._groups.clear()
        return callbacks

    @contextmanager
    def pause(self):
        """Temporarily pause all callbacks."""
        logger.debug('Pausing callbacks...')
        callbacks = self.unregister()
        try:
            yield
        finally:
            for callback in callbacks:
                logger.debug('Unpausing all callbacks...')
                callback.register()

    @property
    def gui(self):
        """Get the GUI the class belongs to.
        It may return None if the GUI is deleted.
        """
        return self._gui()
