"""
CLI tests for skills/bmad-init/scripts/bmad-status.py.

Verifies the status dashboard script can be invoked as a subprocess
and produces expected output for various inputs.
"""

import subprocess
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PLUGIN_ROOT / "skills" / "bmad-init" / "scripts" / "bmad-status.py"
PROJECT_ROOT = PLUGIN_ROOT  # has .a0proj directory


class TestHelpRuns(unittest.TestCase):
    """--help must exit cleanly with usage text."""

    def test_help_runs(self):
        proc = subprocess.run(
            ["python3", str(SCRIPT), "--help"],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--project-path", proc.stdout)


class TestStatusWithProjectRoot(unittest.TestCase):
    """Run with --project-path pointing to the plugin root (has .a0proj)."""

    def test_status_with_project_root(self):
        proc = subprocess.run(
            ["python3", str(SCRIPT), "--project-path", str(PROJECT_ROOT)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, f"stderr: {proc.stderr}")
        # Must report agent count
        self.assertIn("agent", proc.stdout.lower())

    def test_status_reports_state(self):
        proc = subprocess.run(
            ["python3", str(SCRIPT), "--project-path", str(PROJECT_ROOT)],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(proc.returncode, 0, f"stderr: {proc.stderr}")
        # Must contain phase/state info
        output_lower = proc.stdout.lower()
        self.assertTrue(
            "phase" in output_lower or "state" in output_lower or "ready" in output_lower,
            f"Output must mention phase/state: {proc.stdout[:200]}",
        )


class TestStatusWithInvalidPath(unittest.TestCase):
    """Running with a non-existent path must handle gracefully."""

    def test_status_with_invalid_path(self):
        proc = subprocess.run(
            ["python3", str(SCRIPT), "--project-path", "/nonexistent/path/xyz"],
            capture_output=True, text=True, timeout=30,
        )
        # Script should not crash with traceback
        self.assertEqual(proc.returncode, 0)
        # Should still produce some output
        self.assertIn("BMAD", proc.stdout)


if __name__ == "__main__":
    unittest.main()
