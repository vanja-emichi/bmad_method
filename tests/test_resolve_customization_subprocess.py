"""
Subprocess tests for scripts/resolve_customization.py.

Verifies the CLI script can be invoked as a subprocess and returns valid JSON.
"""

import json
import subprocess
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "scripts" / "resolve_customization.py"
SKILL_WITH_TOML = PLUGIN_ROOT / "skills" / "bmad-bmm" / "workflows" / "1-analysis" / "create-product-brief"


class TestHelpRuns(unittest.TestCase):
    """--help must exit cleanly with usage text."""

    def test_help_runs(self):
        proc = subprocess.run(
            ["python3", str(SCRIPT), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--skill", proc.stdout)


class TestSubprocessWithSkill(unittest.TestCase):
    """Run with a real skill dir that has customize.toml."""

    def test_subprocess_with_skill_returns_json(self):
        proc = subprocess.run(
            ["python3", str(SCRIPT), "--skill", str(SKILL_WITH_TOML)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, f"stderr: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertIsInstance(data, dict)
        # customize.toml for create-product-brief has a workflow key
        self.assertIn("workflow", data)

    def test_subprocess_with_key_arg(self):
        proc = subprocess.run(
            ["python3", str(SCRIPT), "--skill", str(SKILL_WITH_TOML), "--key", "workflow"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, f"stderr: {proc.stderr}")
        data = json.loads(proc.stdout)
        self.assertIsInstance(data, dict)
        # workflow section should have persistent_facts or brief_template
        self.assertTrue(
            "persistent_facts" in data.get("workflow", data) or "brief_template" in data.get("workflow", data),
            f"Expected workflow fields in {data}",
        )


class TestSubprocessMissingSkillArg(unittest.TestCase):
    """Running without --skill must fail with non-zero exit code."""

    def test_subprocess_missing_skill_arg(self):
        proc = subprocess.run(
            ["python3", str(SCRIPT)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("--skill", proc.stderr)


if __name__ == "__main__":
    unittest.main()
