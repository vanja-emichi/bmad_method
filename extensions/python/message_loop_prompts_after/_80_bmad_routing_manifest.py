"""
BmadRoutingManifest — Dynamically build BMAD routing table from all module.yaml files.

Reads from skills/*/module.yaml and skills/bmad-init/core/module.yaml
(single source of truth) instead of CSV files. Uses yaml.safe_load() for parsing.

Injects a compact routing table into extras_temporary["bmad_routing_manifest"]
for bmad-master to use on every message loop.

Migration: CSV → YAML (Bundle 1, Slice 1.3)
Source: SPEC.md §1.3, §Migration Guide
Supersedes: ADR-0001 (CSV canonical routing)
"""

import logging
import traceback
from pathlib import Path
import re
import importlib.util as _ilu
import yaml

from helpers.extension import Extension
from helpers import files
from agent import LoopData

log = logging.getLogger(__name__)

# Dynamic path resolution — works regardless of install method (plugin, symlink, dev)
_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
_SKILLS_DIR = _PLUGIN_ROOT / "skills"
_BMAD_CONFIG_DIR = _PLUGIN_ROOT / "skills" / "bmad-init" / "_config"

# Load shared state parser via importlib to avoid name collision with A0's 'helpers' package
_core_path = str(_PLUGIN_ROOT / "helpers" / "bmad_status_core.py")
_spec = _ilu.spec_from_file_location("bmad_status_core", _core_path)
if _spec is None:
    raise ImportError(f"Cannot load bmad_status_core from {_core_path}")
_core_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_core_mod)
_read_state = _core_mod.read_state

# Module-level caches — keyed by (path_str, mtime_ns) for auto-invalidation on file change
_MAX_CACHE_ENTRIES = 128
_alias_cache: dict = {}
_yaml_cache: dict = {}


def _evict_if_full(cache: dict) -> None:
    """Remove oldest entries when cache exceeds _MAX_CACHE_ENTRIES."""
    if len(cache) > _MAX_CACHE_ENTRIES:
        # Remove oldest half (FIFO eviction — good enough for mtime-keyed caches)
        keys_to_remove = list(cache.keys())[:len(cache) // 2]
        for k in keys_to_remove:
            del cache[k]

# ── Security validation helpers ────────────────────────────────────────────────

_SAFE_GLOB_RE = re.compile(r'^[\w\-.*?\[\]{}]+$')


def _sanitize_glob_pattern(pattern: str) -> str:
    """Validate a glob pattern from YAML before passing to Path.glob().
    Rejects patterns with path traversal (..), absolute paths, or unsafe chars.
    Returns the pattern if safe, or '*.md' as fallback.
    """
    if not pattern:
        return '*.md'
    # Reject absolute paths and path traversal
    if pattern.startswith('/') or '..' in pattern:
        log.warning("Rejected unsafe glob pattern (traversal/absolute): %s", pattern)
        return '*.md'
    # Reject patterns with suspicious characters
    if not _SAFE_GLOB_RE.match(pattern):
        log.warning("Rejected unsafe glob pattern (invalid chars): %s", pattern)
        return '*.md'
    return pattern


def _validate_path_in_project(resolved: Path, project_root: Path | None = None) -> bool:
    """Ensure a resolved path stays inside the project root.

    Rejects any '..' sequence (defense in depth) and, when ``project_root`` is
    provided, also rejects paths that escape that root after canonicalization —
    covering absolute paths, symlink targets, and alias entries pointing outside
    the project (e.g. '../../../etc/passwd').
    """
    try:
        raw = str(resolved)
        if '..' in raw:
            return False
        if project_root is None:
            return True
        root = Path(project_root).resolve()
        candidate = Path(resolved)
        target = (candidate if candidate.is_absolute() else root / candidate).resolve()
        return target.is_relative_to(root)
    except (ValueError, OSError, RuntimeError):
        return False

BMAD_MASTER_PROFILE = "bmad-master"


# Canonical phase bucket keys — single source of truth for phase-bucket dicts
PHASE_BUCKETS = ["1-analysis", "2-planning", "3-solutioning", "4-implementation"]

# Phase → relevant modules map (derived from PHASE_BUCKETS)
PHASE_MODULES = {
    "ready":            ["core", "bmm", "bmb", "tea", "cis"],
    **{PHASE_BUCKETS[i]: v for i, v in enumerate([
        ["core", "bmm", "cis"],       # 1-analysis
        ["core", "bmm", "cis"],       # 2-planning
        ["core", "bmm", "tea", "cis"], # 3-solutioning
        ["core", "bmm", "tea", "cis"], # 4-implementation
    ])},
    "bmb":              ["core", "bmb"],
    "cis":              ["core", "cis"],
}


def _read_yaml_cached(yaml_path: Path) -> dict:
    """Read and parse YAML file with mtime-keyed cache invalidation.
    Returns parsed dict from yaml.safe_load().
    """
    global _yaml_cache
    mtime_ns = yaml_path.stat().st_mtime_ns
    cache_key = (str(yaml_path), mtime_ns)
    if cache_key not in _yaml_cache:
        text = yaml_path.read_text(encoding="utf-8")
        _yaml_cache[cache_key] = yaml.safe_load(text)
        _evict_if_full(_yaml_cache)
    return _yaml_cache[cache_key]


def _discover_yaml_files() -> list[Path]:
    """Discover all module.yaml files for routing.
    Finds skills/*/module.yaml (bmm, tea, cis, bmb) and
    skills/bmad-init/core/module.yaml (init/core).
    """
    yaml_files = sorted(_SKILLS_DIR.glob("*/module.yaml"))
    # Add init/core/module.yaml if not already found by glob
    init_core = _SKILLS_DIR / "bmad-init" / "core" / "module.yaml"
    if init_core.exists() and init_core not in yaml_files:
        yaml_files.append(init_core)
    return yaml_files


def _resolve_state_file(agent) -> Path | None:
    """Resolve the BMAD state file from the active project context."""
    try:
        from helpers import projects
        project_name = projects.get_context_project_name(agent.context)
        if project_name:
            folder = Path(projects.get_project_folder(project_name))
            state = folder / ".a0proj" / "instructions" / "02-bmad-state.md"
            if state.exists():
                return state
    except Exception:
        pass

    return None


def _resolve_project_root(agent) -> Path | None:
    """Resolve the active project folder for containment checks."""
    try:
        from helpers import projects
        project_name = projects.get_context_project_name(agent.context)
        if project_name:
            return Path(projects.get_project_folder(project_name)).resolve()
    except Exception:
        pass
    return None


def _collect_routing_rows(active_modules: list | None, yaml_files: list | None = None) -> list[str]:
    """
    Read all module.yaml files and return routing row strings.
    Filters by active_modules if provided. Uses _yaml_cache with mtime invalidation.
    Output format is identical to the CSV version — this is a contract.
    """
    routing_rows = []

    # Discover all module.yaml files sorted by path (use provided list or discover)
    if yaml_files is None:
        yaml_files = _discover_yaml_files()

    for yaml_path in yaml_files:
        try:
            data = _read_yaml_cached(yaml_path)
            if not data or "workflows" not in data:
                continue

            for wf in data["workflows"]:
                module = wf.get("module", "").strip()
                row_phase = wf.get("phase", "").strip()
                # YAML fields map 1:1 to CSV columns (SPEC §Migration Guide)
                name = wf.get("display-name", "").strip()
                code = wf.get("menu-code", "").strip()
                description = wf.get("description", "").strip()
                # action = canonical skill name for skills_tool:load
                # args = direct workflow file path fallback when action is empty
                action = wf.get("action", "").strip()
                args = wf.get("args", "").strip()
                # agent column maps to profile name for call_subordinate
                agent_name = wf.get("skill", "").strip()
                # Agent display name — fallback to agent_name
                agent_display = (
                    wf.get("agent-display-name", "").strip()
                    or agent_name
                )

                # Skip rows without agent — standalone tools invoked directly
                if not agent_name:
                    continue

                # Filter by active modules if phase-specific
                if active_modules and module not in active_modules:
                    continue

                desc_suffix = f" — {description}" if description else ""
                # skill: tells BMad Master which skill to load_tool; args: direct file fallback
                skill_suffix = f" [skill:{action}]" if action else (f" [args:{args}]" if args else "")
                routing_rows.append(
                    f"`{code}` {name} [{module}/{row_phase}] → {agent_name} ({agent_display}){skill_suffix}{desc_suffix}"
                )

        except Exception:
            continue

    return routing_rows



# ── Artifact completion detection helpers (AC-01 through AC-06) ──────────────

def _parse_alias_map(config_path: Path) -> dict:
    """Parse 01-bmad-config.md Path Conventions table.
    Returns alias_key (without braces) → resolved absolute path string.
    AC-01: alias resolution. AC-06: cached by (path, mtime_ns).
    """
    global _alias_cache
    try:
        mtime_ns = config_path.stat().st_mtime_ns
    except OSError:
        return {}
    cache_key = (str(config_path), mtime_ns)
    if cache_key in _alias_cache:
        return _alias_cache[cache_key]

    alias_map: dict = {}
    try:
        for line in config_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            parts = [p.strip() for p in line.split("|")]
            # Expected: | `{alias}` | /resolved/path/ |
            if len(parts) < 4:
                continue
            alias_raw = parts[1].strip("`")  # `{planning_artifacts}` → {planning_artifacts}
            path_raw = parts[2].strip().strip("`")  # strip markdown code-span backticks
            if alias_raw.startswith("{") and alias_raw.endswith("}"):
                alias_key = alias_raw[1:-1]  # strip braces → planning_artifacts
                if path_raw and not path_raw.startswith("-"):
                    alias_map[alias_key] = path_raw
    except Exception:
        pass

    _alias_cache[cache_key] = alias_map
    _evict_if_full(_alias_cache)
    return alias_map


def _resolve_dir(location_raw: str, alias_map: dict, project_root: Path | None = None) -> "Path | None":
    """Resolve output-location alias → absolute Path.
    Handles pipe-separated values (uses first segment).
    AC-02, AC-05: returns None if alias missing (graceful degradation).
    """
    location = location_raw.split("|")[0].strip()
    if not location:
        return None
    resolved = alias_map.get(location)
    if not resolved:
        return None
    p = Path(resolved)
    if not _validate_path_in_project(p, project_root):
        log.warning("Rejected alias path outside project: %s", resolved)
        return None
    return p


def _scan_artifact_existence(yaml_files: list, alias_map: dict, project_root: Path | None = None) -> dict:
    """Scan filesystem for required phase-gating artifacts.
    AC-02, AC-03: glob output dirs, return phase → (found: bool, note: str).
    Phase is complete if ANY required=true artifact for that phase is found.
    AC-06: uses Path.glob() for performance.
    """
    phase_map: dict = {k: (False, "no required artifact found") for k in PHASE_BUCKETS}
    for yaml_path in yaml_files:
        try:
            data = _read_yaml_cached(yaml_path)
            if not data or "workflows" not in data:
                continue
            for wf in data["workflows"]:
                # AC-03: only required=true rows gate phase completion
                required = wf.get("required", False)
                if not required:
                    continue
                row_phase = wf.get("phase", "").strip()
                # Map phase value to bucket by prefix ("1-", "2-", etc.)
                bucket = next((k for k in phase_map if row_phase.startswith(k[:2])), None)
                if not bucket:
                    continue
                if phase_map[bucket][0]:
                    continue  # AC-03: already found for this bucket — skip
                output_location = wf.get("output-location", "").strip()
                if not output_location:
                    continue
                # AC-05: skip row if alias cannot be resolved
                resolved_dir = _resolve_dir(output_location, alias_map, project_root)
                if not resolved_dir or not resolved_dir.exists():
                    continue
                # AC-02: glob for artifact
                pattern = wf.get("outputs", "").strip()
                if not pattern or pattern == "*":
                    pattern = "*.md"
                else:
                    pattern = _sanitize_glob_pattern(pattern)
                matches = list(resolved_dir.glob(pattern))  # AC-06: Path.glob()
                if matches:
                    phase_map[bucket] = (True, matches[0].name)
        except Exception:
            continue  # AC-05: never raise
    return phase_map


def _build_completed_phases_text(phase_map: dict) -> str:
    """Format phase completion map as readable EXTRAS section.
    AC-04: one line per phase, bool + parenthetical note.
    """
    lines = ["## Completed Phases (filesystem scan)"]
    for phase, (found, note) in phase_map.items():
        status = "true" if found else "false"
        lines.append(f"{phase}: {status}  ({note})")
    return "\n".join(lines)


def _build_staleness_warnings(alias_map: dict) -> str:
    """Compare mtime of parent→child artifact pairs and return staleness warning lines.
    Appended to the BMAD routing manifest in EXTRAS as advisory-only information.
    Graceful degradation: missing files or alias errors are silently skipped.
    Never raises — must not block routing under any circumstances.
    """
    warnings = []
    try:
        planning_raw = alias_map.get("planning_artifacts")
        implementation_raw = alias_map.get("implementation_artifacts")
        if not planning_raw or not implementation_raw:
            return ""

        planning_path = Path(planning_raw)
        implementation_path = Path(implementation_raw)

        # ── Locate PRD ────────────────────────────────────────────────────────
        prd_file = None
        prd_direct = planning_path / "prd.md"
        if prd_direct.exists():
            prd_file = prd_direct
        else:
            prd_candidates = [
                f for f in planning_path.glob("prd-*.md")
                if "validation" not in f.name and "status" not in f.name
            ]
            if prd_candidates:
                prd_file = max(prd_candidates, key=lambda f: f.stat().st_mtime)

        # ── Locate Architecture doc ───────────────────────────────────────────
        arch_file = None
        arch_candidates = list(planning_path.glob("architecture-*.md"))
        if arch_candidates:
            arch_file = max(arch_candidates, key=lambda f: f.stat().st_mtime)

        # ── Locate Sprint Plan ────────────────────────────────────────────────
        sprint_file = None
        sprint_candidates = list(implementation_path.glob("sprint-plan*.md"))
        if sprint_candidates:
            sprint_file = max(sprint_candidates, key=lambda f: f.stat().st_mtime)

        # ── Rule 1: PRD newer than Architecture ───────────────────────────────
        if prd_file and arch_file:
            if prd_file.stat().st_mtime > arch_file.stat().st_mtime:
                warnings.append(
                    f"\u26a0\ufe0f Architecture may be stale "
                    f"\u2014 PRD ({prd_file.name}) was updated after architecture ({arch_file.name})"
                )

        # ── Rule 2: Architecture newer than Sprint Plan ───────────────────────
        if arch_file and sprint_file:
            if arch_file.stat().st_mtime > sprint_file.stat().st_mtime:
                warnings.append(
                    f"\u26a0\ufe0f Sprint plan may be stale "
                    f"\u2014 Architecture ({arch_file.name}) was updated after sprint plan ({sprint_file.name})"
                )

        # ── Rule 3: PRD newer than Sprint Plan (independent of arch) ──────────
        if prd_file and sprint_file:
            if prd_file.stat().st_mtime > sprint_file.stat().st_mtime:
                # Only emit if Rule 2 did not already cover it
                arch_covers = (
                    arch_file is not None
                    and arch_file.stat().st_mtime > sprint_file.stat().st_mtime
                )
                if not arch_covers:
                    warnings.append(
                        f"\u26a0\ufe0f Sprint plan may be stale "
                        f"\u2014 PRD ({prd_file.name}) was updated after sprint plan ({sprint_file.name})"
                    )

    except Exception:
        log.warning("BMAD routing: staleness check failed: %s", traceback.format_exc())

    if not warnings:
        return ""
    return "\n\n## Artifact Staleness Warnings\n" + "\n".join(warnings)

class BmadRoutingManifest(Extension):
    """
    Injects compact BMAD routing manifest into bmad-master context.

    Phase-aware: loads all modules when phase=ready, otherwise loads
    phase-relevant modules only.

    Reads dynamically from all module.yaml files — no compiled
    aggregate needed. Adding a workflow to module.yaml is immediately
    reflected in the routing table without any sync step.
    """

    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        if not self.agent or self.agent.config.profile != BMAD_MASTER_PROFILE:
            return

        try:
            # Inject resolved paths so prompts can reference them
            loop_data.extras_temporary["bmad_paths"] = (
                f"bmad_config_dir: {_BMAD_CONFIG_DIR}\n"
                f"bmad_plugin_root: {_PLUGIN_ROOT}"
            )

            # Read current phase from state file
            phase = "ready"
            active_modules = None
            state_path = _resolve_state_file(self.agent)

            # ── Not initialized: inject guidance, skip routing table ────────────
            if not state_path:
                loop_data.extras_temporary["bmad_not_initialized"] = (
                    "# BMAD Project Status: NOT INITIALIZED\n"
                    "This project has not been initialized with BMAD yet.\n"
                    "The user must run `bmad init` before any BMAD workflows can begin.\n"
                    "IMPORTANT: On the user's next message, respond by explaining that BMAD "
                    "is not initialized for this project and instruct them to run `bmad init`. "
                    "Do NOT show the workflow menu or attempt any routing."
                )
                return

            if state_path:
                state_result = _read_state(state_path)
                phase = state_result["phase"]
                active_modules = PHASE_MODULES.get(phase)

            # Single discovery per execute() — reused for routing rows and artifact scan
            yaml_files = _discover_yaml_files()

            # Collect routing rows from all module.yaml files
            routing_rows = _collect_routing_rows(active_modules, yaml_files)

            if not routing_rows:
                return

            phase_note = (
                f"(phase={phase}, showing modules: {', '.join(active_modules)})"
                if active_modules
                else "(all modules)"
            )
            routing_table = "\n".join(routing_rows)

            manifest_prompt = (
                f"# BMAD Routing Table {phase_note}\n"
                f"Match user request → read agent-name → map to profile → call_subordinate.\n"
                f"Multiple matches → show list, ask user to pick. Never route from memory.\n\n"
                f"{routing_table}"
            )

            # ── Artifact completion detection (AC-01 through AC-06) ────────────
            try:
                config_path = state_path.parent / "01-bmad-config.md"  # AC-01
                project_root = _resolve_project_root(self.agent)
                if config_path.exists():
                    alias_map = _parse_alias_map(config_path)  # AC-06: cached
                    phase_map = _scan_artifact_existence(
                        yaml_files, alias_map, project_root
                    )  # AC-02, AC-03
                    completed_text = _build_completed_phases_text(phase_map)  # AC-04
                    manifest_prompt += f"\n\n{completed_text}"
                    staleness_text = _build_staleness_warnings(alias_map)
                    if staleness_text:
                        manifest_prompt += staleness_text
                else:
                    manifest_prompt += "\n\n## Completed Phases (filesystem scan)\ncompleted_phases: unavailable (config not found)"  # AC-05
            except Exception:
                log.warning("Artifact scan failed: %s", traceback.format_exc())
                manifest_prompt += "\n\n## Completed Phases (filesystem scan)\ncompleted_phases: unavailable (scan error)"  # AC-05

            loop_data.extras_temporary["bmad_routing_manifest"] = manifest_prompt

        except Exception:
            log.warning("BMAD routing: execute failed: %s", traceback.format_exc())
