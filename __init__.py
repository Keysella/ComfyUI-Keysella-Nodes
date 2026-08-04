"""
ComfyUI-Keysella-Nodes package entry point.

Node implementations live under nodes/<category>/<node_file>.py (folder
names use hyphens, e.g. nodes/prompt-nodes/, so they are loaded via
importlib.util.spec_from_file_location instead of regular package imports).

To add a new node:
1. Create/reuse a category folder under nodes/, e.g. nodes/prompt-nodes/.
2. Add a module there exposing NODE_CLASS_MAPPINGS and
   NODE_DISPLAY_NAME_MAPPINGS (see nodes/prompt-nodes/prompt_perfectionist.py).
3. Add its relative path to the _NODE_MODULES list below.
"""

import importlib.util
import pathlib

_HERE = pathlib.Path(__file__).parent

# Relative paths (from this file) to every node module that should be loaded.
_NODE_MODULES = [
    "nodes/prompt-nodes/prompt_perfectionist.py",
    "nodes/prompt-nodes/prompt-from-file-loader.py",
    "nodes/prompt-nodes/prompt-file-editor.py",
]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


def _load_module(relative_path: str):
    path = _HERE / relative_path
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


for _rel_path in _NODE_MODULES:
    _module = _load_module(_rel_path)
    NODE_CLASS_MAPPINGS.update(getattr(_module, "NODE_CLASS_MAPPINGS", {}))
    NODE_DISPLAY_NAME_MAPPINGS.update(getattr(_module, "NODE_DISPLAY_NAME_MAPPINGS", {}))

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]
