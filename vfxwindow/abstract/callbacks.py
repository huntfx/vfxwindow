from __future__ import absolute_import

import logging
import weakref
from collections import defaultdict, namedtuple
from contextlib import contextmanager
from functools import partial, wraps

from ..exceptions import CallbackAliasNotFoundError, CallbackAliasExistsError

logger = logging.getLogger(__name__)


class Alias(object):
    """Create a callback alias."""

    __slots__ = ['_register', '_unregister', '_intercept', '_contains']

    def __init__(self, register, unregister, intercept=None, contains=None):
        """Setup the alias.
        One alias can be the driving force behind multiple callbacks.

        Parameters:
            register (callable): Function to register the callback.
            unregister (callable): Function to unregister the callback.
                By default it takes in the result from the register
                function, but this can be overridden if required.
            itercept (callable, optional): Determine if should skip.
                Returning True will intercept and stop the callback.
                It should take the same args and kwargs as `register`.
            contains (callable, optional): Check if registered.
                If not set, a basic check will be used.
                It should take the same args and kwargs as `register`.
        """
        self._register = register
        self._unregister = unregister
        self._intercept = intercept
        self._contains = contains

    @property
    def register(self):
        """Get the register callback function."""
        return self._register

    @property
    def unregister(self):
        """Get the unregister callback function."""
        return self._unregister

    def intercept(self, *args, **kwargs):
        """Determine if the callback should be intercepted."""
        if self._intercept is None:
            return False
        return self._intercept(*args, **kwargs)

    @property
    def contains(self):
        """Get the register check function if it's set."""
        return self._contains


class CallbackProxy(object):
    """Hold the callback data for easy registering/unregistering."""

    def __init__(self, name, alias, func, args=None, kwargs=None):
        """Create a proxy.

        Parameters:
            name (str): Name to give to the proxy to display in messages.
            alias (Alias): Contains the registered functions.
            func (callable): Function to register.
            args (tuple, optional): User defined for the register function.
            kwargs (dict, optional): User defined for the register function.
            itercept (callable, optional): Determine if the callback should be stopped.
                Returning True will intercept and stop the callback.
                It should take the same args and kwargs as `func`.
        """
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}

        self._id = None
        self._name = name
        self._alias = alias
        self._args = args
        self._kwargs = kwargs

        self._registered = False
        self._result = None

        @wraps(func.func if isinstance(func, partial) else func)
        def runCallback(*args, **kwargs):
            """Run the callback function."""
            if not alias.intercept(*args, **kwargs):
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

    @property
    def alias(self):
        """Get the alias."""
        return self._alias

    def forceUnregister(self):
        """Unregister the callback without any extra checks.
        This may require overriding.
        """
        self.alias.unregister(self._result)

    @property
    def registered(self):
        """Determine if the callback is registered."""
        if self.alias.contains is not None:
            return self.alias.contains(self.func, *self._args, **self._kwargs)
        return self._registered

    def register(self):
        """Register the callback."""
        if not self.registered:
            logger.info('Registering: %s', self._name)
            self._result = self.alias.register(self.func, *self._args, **self._kwargs)
            self._registered = True
        return self

    def unregister(self):
        """Unregister the callback."""
        if self.registered:
            logger.info('Unregistering: %s', self._name)
            self.forceUnregister()
            self._registered = False
        return self


class CallbackAliases(object):
    """Set aliases for callbacks."""

    __slots__ = ['_data', '_function']

    def __init__(self):
        self._data = {}
        self._function = None

    def __repr__(self):
        return repr(self.items())

    def __str__(self):
        return str(self.items())

    def __getitem__(self, alias):
        """Get the callback for the current alias.

        Parameters:
            alias (str): Callback alias.

        Returns:
            CallbackProxy instance.

        Raises:
            KeyError if alias not found or can't be determined.

        >>> aliases = CallbackAliases()
        >>> register = unregister = lambda *args, **kwargs: None
        >>> aliases['x.y'] = (register, unregister)
        >>> aliases['x.y']
        (register, unregister)

        If the alias is too detailed (eg. "file.new.before" when only
        "file.new" is supported), then assuming no other aliases exist
        at the same level, then the parent one will be returned.

        >>> aliases['x.y.z']
        (register, unregister)

        If the alias is not detailed anough (eg. "file.new" when
        "file.new.after" is supported), then it will read the parent
        alias if a single one exists. If multiple possibilities exist,
        then for safety it won't guess which to use and returns None.

        >>> aliases['x']
        (register, unregister)

        >>> aliases['x.y2'] = (register, unregister)
        >>> aliases['x']
        None

        >>> aliases['x'] = aliases['x.y']
        >>> aliases['x']
        (register, unregister)
        """
        # Get alias for every level up to current
        current = self
        func = current._function
        for part in alias.split('.'):
            if part not in current._data:
                break
            current = current._data[part]
            if current._function is not None:
                func = current._function

        # If no functions found, then search children
        if func is None:
            stack = list(current._data.values())
            while stack:
                item = stack.pop()
                stack.extend(item._data.values())
                if item._function:
                    # Fail if multiple found
                    if func is not None:
                        raise CallbackAliasNotFoundError(alias)
                    func = item._function

        if func is None:
            raise CallbackAliasNotFoundError(alias)

        return func

    def __setitem__(self, alias, data):
        """Create a new alias.

        Parameters:
            alias (str): Alias to assign the callback to.

            data (tuple): Data to pass to `Alias`.
                It must be the `Alias` type or of a tuple that matches
                the arguments to the class.

                `register` parameters are `(func, *args, **kwargs)`.
                `unregister` parameters are `(callbackID)`.
                `intercept` parameters must match that of `func`.
                `extra` parameters are `(any)`.

        Raises:
            AliasAlreadyExistsError: If the alias is already registered.
        """
        # Walk to the correct point
        current = self
        for part in alias.split('.'):
            if part not in current._data:
                current._data[part] = CallbackAliases()
            current = current._data[part]

        if current._function is not None:
            raise CallbackAliasExistsError('alias already exists for {}'.format(alias))

        if not isinstance(data, Alias):
            data = Alias(*data)
        current._function = data

    def __delitem__(self, alias):
        """Delete an alias.
        If a child alias exists, it will not be deleted.
        """
        # Create a stack of each child until the requested data
        stack = []
        data = self._data
        for part in alias.split('.'):
            if part not in data:
                raise KeyError(alias)
            stack.append((part, data))
            data = data[part]._data

        for i, (part, data) in enumerate(reversed(stack)):
            # Delete the requested alias
            if not i:
                # If no alias exists, raise a KeyError
                if data[part]._function is None:
                    raise KeyError(alias)
                data[part]._function = None

            # Clean up empty aliases
            if data[part]:
                break
            else:
                del data[part]

    def __contains__(self, alias):
        """Check if an alias exists."""
        current = self
        for part in alias.split('.'):
            if part not in current._data:
                return False
            current = current._data[part]
        return current._function is not None

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def keys(self, _prefix=''):
        """Get all the keys."""
        keys = []
        for k, v in self._data.items():
            if v._function is not None:
                keys.append(_prefix + k)
            keys.extend(v.keys(_prefix=_prefix + k + '.'))
        return keys

    def values(self):
        return [self.__getitem__(k) for k in self.keys()]

    def items(self):
        return [(k, self.__getitem__(k)) for k in self.keys()]


class AbstractCallbacks(object):
    """Base class for callbacks."""

    CallbackProxy = CallbackProxy

    def __init__(self, gui, _aliases=None):
        if isinstance(gui, weakref.ReferenceType):
            self._gui = gui
        else:
            self._gui = weakref.ref(gui)
        self._callbacks = []
        self._groups = defaultdict(self._new)

        if _aliases is None:
            self.aliases = CallbackAliases()
            self._setupAliases()
        else:
            self.aliases = _aliases

    def _new(self):
        return type(self)(self._gui, _aliases=self.aliases)

    def _setupAliases(self):
        """Setup callback aliases.

        This is done at a class instance level so that users may choose
        to modify or register callbacks for an individual window without
        affecting anything else.

        Example:
            >>> self.callbacks.aliases['custom.event'] = (reg, unreg)
            >>> self.callbacks.add('custom.event', myFunc)
        """

    def __getitem__(self, group):
        return self._groups[group]

    def __delitem__(self, group):
        self._groups[group].delete()
        del self._groups[group]

    def __iter__(self):
        return iter(self._groups)

    def __contains__(self, other):
        return other in self._groups

    def keys(self):
        return self._groups.keys()

    def values(self):
        return self._groups.values()

    def items(self):
        return self._groups.items()

    def add(self, alias, func, *args, **kwargs):
        """Add a pre-defined callback."""
        data = self.aliases[alias]
        callback = self.CallbackProxy(alias, alias=data, func=func, args=args, kwargs=kwargs)
        if self.registerAvailable:
            callback.register()
        self._callbacks.append(callback)
        return callback

    @property
    def registerAvailable(self):
        """Determine if registering is possible right now."""
        return True

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
