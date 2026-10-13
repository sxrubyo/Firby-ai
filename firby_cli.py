#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
firby_cli.py — CLI v8.0 Enterprise (Facade Delegation Entrypoint).
"""
from __future__ import annotations
import sys
import os
from types import ModuleType

import firby_cli_common as common
import firby_cli_instances as instances
import firby_cli_runtime as runtime

class _CLIFacadeModule(ModuleType):
    def __getattr__(self, name: str):
        if hasattr(common, name):
            return getattr(common, name)
        if hasattr(instances, name):
            return getattr(instances, name)
        if hasattr(runtime, name):
            return getattr(runtime, name)
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

    def __setattr__(self, name: str, value: any):
        if hasattr(common, name):
            setattr(common, name, value)
        elif hasattr(instances, name):
            setattr(instances, name, value)
        elif hasattr(runtime, name):
            setattr(runtime, name, value)
        else:
            super().__setattr__(name, value)

for mod in (common, instances, runtime):
    for k in dir(mod):
        if not k.startswith("__"):
            globals()[k] = getattr(mod, k)

sys.modules[__name__].__class__ = _CLIFacadeModule

if __name__ == "__main__":
    raise SystemExit(main() or 0)
