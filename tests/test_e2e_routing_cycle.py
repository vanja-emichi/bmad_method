"""
E2E Routing Cycle Tests - verify full YAML -> routing manifest -> code lookup cycle.

Tests the routing extension's ability to load real module.yaml files,
build a routing table, and find workflow paths by menu code.
"""

import sys
import types
import unittest
from pathlib import Path

import yaml

# -- Save sys.modules state to avoid polluting other tests --
_stub_keys = (
    "helpers", "helpers.files", "helpers.projects",
    "helpers.extension", "agent",
)
_saved_modules = {k: sys.modules[k] for k in _stub_keys if k in sys.modules}

# -- Stub Agent Zero runtime modules before importing extension --
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

# Now import the functions under test
from extensions.python.message_loop_prompts_after._80_bmad_routing_manifest import (
    _read_yaml_cached,
    _discover_yaml_files,
    _collect_routing_rows,
    _sanitize_glob_pattern,
)
import extensions.python.message_loop_prompts_after._80_bmad_routing_manifest as _ext80

# -- Restore sys.modules so other tests see real modules --
for k in _stub_keys:
    if k in _saved_modules:
        sys.modules[k] = _saved_modules[k]
    elif k in sys.modules:
        del sys.modules[k]

SKILLS_DIR = PLUGIN_ROOT / "skills"


class TestYamlLoadAndParse(unittest.TestCase):
    """Load a real module.yaml file and verify it has expected fields."""

    def test_yaml_load_and_parse(self):
        cis_yaml = SKILLS_DIR / "bmad-cis" / "module.yaml"
        self.assertTrue(cis_yaml.exists(), f"module.yaml not found at {cis_yaml}")

        data = _read_yaml_cached(cis_yaml)
        self.assertIsInstance(data, dict)
        self.assertIn("code", data, "module.yaml must have a code field")
        self.assertIn("workflows", data, "module.yaml must have a workflows field")
        self.assertEqual(data["code"], "cis")
        self.assertIsInstance(data["workflows"], list)
        self.assertGreater(len(data["workflows"]), 0, "workflows list must not be empty")

        wf = data["workflows"][0]
        for field in ("module", "skill", "display-name", "menu-code", "action"):
            self.assertIn(field, wf, f"workflow entry must have {field} field")


class TestRoutingTableHasEntries(unittest.TestCase):
    """Build routing table from actual skills/ directory and verify entries."""

    def test_routing_table_has_entries(self):
        rows = _collect_routing_rows(active_modules=None)
        self.assertIsInstance(rows, list)
        self.assertGreater(len(rows), 0, "routing table must have at least one entry")
        for row in rows:
            self.assertIsInstance(row, str)
            self.assertRegex(row, r"^`[A-Z]{2,}`", f"row must start with menu code: {row[:60]}")

    def test_discover_yaml_finds_modules(self):
        yaml_files = _discover_yaml_files()
        self.assertGreater(len(yaml_files), 0)
        names = [p.parent.name for p in yaml_files]
        for expected in ("bmad-cis", "bmad-bmm", "bmad-tea", "bmad-bmb"):
            self.assertIn(expected, names, f"{expected} module.yaml must be discovered")


class TestFindWorkflowByCode(unittest.TestCase):
    """Search routing table for a known menu code and verify workflow path."""

    @classmethod
    def setUpClass(cls):
        cls.rows = _collect_routing_rows(active_modules=None)

    def test_find_brainstorming_code_bs(self):
        bs_rows = [r for r in self.rows if r.startswith("`BS`")]
        self.assertGreater(len(bs_rows), 0, "BS menu code must appear in routing table")

    def test_brainstorming_row_has_agent_and_action(self):
        bs_rows = [r for r in self.rows if r.startswith("`BS`")]
        self.assertGreater(len(bs_rows), 0)
        row = bs_rows[0]
        self.assertIn("brainstorming-coach", row)
        self.assertIn("[skill:", row)

    def test_innovation_strategy_code_is(self):
        is_rows = [r for r in self.rows if r.startswith("`IS`")]
        self.assertGreater(len(is_rows), 0, "IS menu code must appear in routing table")


class TestFullCycleYamlToRoute(unittest.TestCase):
    """End-to-end: load YAML -> build table -> find code -> verify agent and action."""

    def test_full_cycle_yaml_to_route(self):
        cis_yaml = SKILLS_DIR / "bmad-cis" / "module.yaml"
        data = _read_yaml_cached(cis_yaml)
        self.assertIn("workflows", data)

        bs_wf = None
        for wf in data["workflows"]:
            if wf.get("menu-code") == "BS":
                bs_wf = wf
                break
        self.assertIsNotNone(bs_wf, "BS workflow must exist in module.yaml")

        rows = _collect_routing_rows(active_modules=None)
        bs_rows = [r for r in rows if r.startswith("`BS`")]
        self.assertGreater(len(bs_rows), 0)

        row = bs_rows[0]
        expected_agent = bs_wf["skill"]
        expected_action = bs_wf["action"]
        self.assertIn(expected_agent, row)
        self.assertIn(f"skill:{expected_action}", row)


class TestSanitizeGlobPattern(unittest.TestCase):
    """Verify glob pattern validation."""

    def test_safe_pattern_passes(self):
        self.assertEqual(_sanitize_glob_pattern("*.md"), "*.md")

    def test_empty_returns_default(self):
        self.assertEqual(_sanitize_glob_pattern(""), "*.md")

    def test_traversal_rejected(self):
        self.assertEqual(_sanitize_glob_pattern("../../etc/passwd"), "*.md")

    def test_absolute_path_rejected(self):
        self.assertEqual(_sanitize_glob_pattern("/etc/passwd"), "*.md")

    def test_unsafe_chars_rejected(self):
        self.assertEqual(_sanitize_glob_pattern("$(cmd)"), "*.md")


if __name__ == "__main__":
    unittest.main()
