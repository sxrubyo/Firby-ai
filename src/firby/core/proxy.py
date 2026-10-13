# -*- coding: utf-8 -*-
"""Shared GlobalProxy utility for lazy resolution of globals.

All modules that need to reference objects from ``src.core.globals``
without triggering circular imports should import ``GlobalProxy``
from this single location instead of duplicating the class.
"""
from __future__ import annotations


class GlobalProxy:
    """Lazy proxy that resolves an attribute from ``src.core.globals`` at access time.

    This avoids circular-import issues during module loading.  Each proxy
    wraps a *name* that will be looked up on ``src.core.globals`` the first
    time any attribute, call, or bool-check is performed.

    Usage::

        from src.firby.core.proxy import GlobalProxy

        Config = GlobalProxy("Config")
        db     = GlobalProxy("db")
    """

    def __init__(self, name: str) -> None:
        self._name = name

    def _target(self):
        import src.core.globals as g
        return getattr(g, self._name)

    def __getattr__(self, attr: str):
        return getattr(self._target(), attr)

    def __bool__(self) -> bool:
        import src.core.globals as g
        return bool(getattr(g, self._name, None))

    def __call__(self, *args, **kwargs):
        return self._target()(*args, **kwargs)

    def __contains__(self, item):
        return item in self._target()

    def __iter__(self):
        return iter(self._target())

    def __len__(self):
        return len(self._target())

    def __getitem__(self, key):
        return self._target()[key]

    def __str__(self):
        return str(self._target())

    def __repr__(self):
        return repr(self._target())



class DynamicGlobalProxy:
    def __init__(self, name):
        self._name = name

    def _get_target(self):
        import sys
        # 1. Try to resolve from src.core.globals first (where init_* overrides them)
        g = sys.modules.get("src.core.globals")
        if g is not None:
            val = getattr(g, self._name, None)
            if val is not None and not isinstance(val, DynamicGlobalProxy):
                return val
        # 2. Fallback to the facade/main module
        facade_name = "firby"
        if g is not None:
            facade_name = getattr(g, "__facade_name__", "firby")
        firby_mod = sys.modules.get(facade_name) or sys.modules.get("firby") or sys.modules.get("__main__")
        if firby_mod is not None:
            val = getattr(firby_mod, self._name, None)
            if val is not None and not isinstance(val, DynamicGlobalProxy):
                return val
        return None

    def __getattr__(self, attr):
        target = self._get_target()
        if target is None:
            raise AttributeError(f"{self._name} is not initialized (Attribute: {attr})")
        return getattr(target, attr)
        
    def __call__(self, *args, **kwargs):
        target = self._get_target()
        if target is None:
            raise TypeError(f"{self._name} is not callable because it is None")
        return target(*args, **kwargs)
        
    def __bool__(self):
        return self._get_target() is not None

    def __contains__(self, item):
        target = self._get_target()
        return item in target if target is not None else False

    def __iter__(self):
        target = self._get_target()
        return iter(target) if target is not None else iter(())

    def __len__(self):
        target = self._get_target()
        return len(target) if target is not None else 0

    def __getitem__(self, key):
        target = self._get_target()
        if target is None:
            raise KeyError(key)
        return target[key]

    def __str__(self):
        return str(self._get_target())

    def __repr__(self):
        return repr(self._get_target())

