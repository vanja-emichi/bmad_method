"""Security tests for _validate_path_in_project — path traversal prevention.

Prove-It pattern: this function was added as a security fix (path traversal
prevention) and MUST have dedicated tests demonstrating it blocks attacks
while allowing legitimate paths.
"""
import sys
import types
import unittest
from pathlib import Path

# -- Stub Agent Zero runtime modules before importing extension --
_stub_keys = (
    "helpers", "helpers.files", "helpers.projects",
    "helpers.extension", "agent",
)
_saved_modules = {k: sys.modules[k] for k in _stub_keys if k in sys.modules}

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLUGIN_ROOT))

_helpers = types.ModuleType("helpers")
_helpers.files = types.ModuleType("helpers.files")
_helpers.projects = types.ModuleType("helpers.projects")
sys.modules.setdefault("helpers", _helpers)
sys.modules.setdefault("helpers.files", _helpers.files)
sys.modules.setdefault("helpers.projects", _helpers.projects)

_ext_mod = types.ModuleType("helpers.extension")
class _Extension:
    pass
_ext_mod.Extension = _Extension
sys.modules.setdefault("helpers.extension", _ext_mod)

_agent_mod = types.ModuleType("agent")
class _LoopData:
    pass
_agent_mod.LoopData = _LoopData
sys.modules.setdefault("agent", _agent_mod)

from extensions.python.message_loop_prompts_after._80_bmad_routing_manifest import (
    _validate_path_in_project,
)

# -- Restore sys.modules so other tests see real modules --
for k in _stub_keys:
    if k in _saved_modules:
        sys.modules[k] = _saved_modules[k]
    else:
        sys.modules.pop(k, None)


class TestValidatePathBlocksTraversal(unittest.TestCase):
    """_validate_path_in_project must reject paths containing '..' sequences."""

    def test_rejects_dotdot_in_path(self):
        """Paths with '..' components must return False."""
        malicious = Path("/tmp/safe/../../../etc/passwd")
        self.assertFalse(_validate_path_in_project(malicious))

    def test_rejects_simple_traversal(self):
        """Simple parent traversal '../../etc/passwd' must return False."""
        self.assertFalse(_validate_path_in_project(Path("../../etc/passwd")))

    def test_rejects_embedded_traversal(self):
        """Embedded '..' in middle of path must return False."""
        self.assertFalse(
            _validate_path_in_project(Path("/home/user/project/../secret"))
        )

    def test_rejects_relative_traversal(self):
        """Relative path with '..' must return False."""
        self.assertFalse(_validate_path_in_project(Path("../sibling/file.md")))


class TestValidatePathAllowsLegitimate(unittest.TestCase):
    """_validate_path_in_project must allow normal paths without '..'."""

    def test_allows_normal_absolute_path(self):
        """Absolute path without '..' must return True."""
        self.assertTrue(
            _validate_path_in_project(Path("/home/user/project/src/file.py"))
        )

    def test_allows_normal_relative_path(self):
        """Relative path without '..' must return True."""
        self.assertTrue(_validate_path_in_project(Path("src/file.py")))

    def test_allows_current_dir_file(self):
        """Simple filename (no directory component) must return True."""
        self.assertTrue(_validate_path_in_project(Path("file.md")))

    def test_allows_deep_nested_path(self):
        """Deeply nested path without '..' must return True."""
        self.assertTrue(
            _validate_path_in_project(
                Path("/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p/file.md")
            )
        )

    def test_allows_dot_slash_path(self):
        """Path starting './' (current dir) must return True — no '..'."""
        self.assertTrue(_validate_path_in_project(Path("./src/file.py")))


class TestValidatePathEdgeCases(unittest.TestCase):
    """Edge cases for _validate_path_in_project."""

    def test_empty_path(self):
        """Empty path (.) has no '..' so should return True."""
        self.assertTrue(_validate_path_in_project(Path(".")))

    def test_path_with_dotdot_in_filename(self):
        """A file literally named '..hidden' contains '..' — should be rejected."""
        self.assertFalse(_validate_path_in_project(Path("..hidden")))
