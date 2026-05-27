from helpers.api import ApiHandler, Request, Response
from pathlib import Path
from datetime import datetime, timedelta
import importlib.util as _ilu

import logging
import threading
_log = logging.getLogger(__name__)


# --- Simple in-memory rate limiter ---
class _RateLimiter:
    """Token-bucket rate limiter for the status endpoint.

    Limits each client (by ctxid or 'anonymous') to a fixed number of
    requests within a rolling time window.  Thread-safe via a lock.
    """

    def __init__(self, max_requests: int = 60, window_seconds: int = 60) -> None:
        self._max = max_requests
        self._window = timedelta(seconds=window_seconds)
        self._buckets: dict[str, list[datetime]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        """Return True if the request is within rate limits."""
        now = datetime.now()
        cutoff = now - self._window
        with self._lock:
            timestamps = self._buckets.setdefault(key, [])
            # Prune entries outside the window
            self._buckets[key] = timestamps = [t for t in timestamps if t > cutoff]
            if len(timestamps) >= self._max:
                return False
            timestamps.append(now)
            return True


_rate_limiter = _RateLimiter(max_requests=60, window_seconds=60)

# Direct importlib load to avoid name collision with A0's own 'helpers' package.
# sys.path manipulation fails here because A0's 'helpers' is already in sys.modules.
_core_path = str(Path(__file__).resolve().parent.parent / "helpers" / "bmad_status_core.py")
_spec = _ilu.spec_from_file_location("bmad_status_core", _core_path)
if _spec is None:
    raise ImportError(f"Cannot load bmad_status_core from {_core_path}")
_core_mod = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_core_mod)
check_agents  = _core_mod.check_agents
check_modules = _core_mod.check_modules
read_state    = _core_mod.read_state
read_tests    = _core_mod.read_tests
SKILL_NAMES   = _core_mod.SKILL_NAMES
AGENT_NAMES   = _core_mod.AGENT_NAMES
PHASE_ACTIONS = _core_mod.PHASE_ACTIONS

# --- Plugin-level paths (fixed, plugin-relative) ---
# Path(__file__).resolve() follows symlinks to the real file location.
_PLUGIN_ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR   = _PLUGIN_ROOT / "agents"
SKILLS_DIR   = _PLUGIN_ROOT / "skills"

# --- Project-level paths (per-request, resolved from active chat context) ---
def _resolve_project_root(ctxid: str | None) -> Path | None:
    """Find the BMAD project root for the currently active chat context.

    Resolution order:
    1. Active context → project name → project folder (correct A0-aware method)
    2. Dev/symlink fallback: walk up from plugin dir looking for .a0proj
    """
    # Stage 1: resolve from active A0 context (the right way)
    if ctxid:
        try:
            from agent import AgentContext
            from helpers import projects
            context = AgentContext.get(ctxid)
            if context:
                project_name = projects.get_context_project_name(context)
                if project_name:
                    folder = Path(projects.get_project_folder(project_name))
                    if (folder / ".a0proj").exists():
                        return folder
                    else:
                        return None  # project exists but no bmad init — show not_initialized
        except Exception:
            pass  # fall through to fallback

    # Stage 2: dev/symlink mode — .a0proj is an ancestor of the real file location
    for parent in [_PLUGIN_ROOT, *_PLUGIN_ROOT.parents]:
        if (parent / ".a0proj").exists():
            return parent

    return None  # no BMAD project found




class BmadStatus(ApiHandler):
    async def process(self, input: dict, request: Request) -> dict | Response:
        try:
            # Rate limiting check
            client_key = input.get("ctxid") or input.get("context_id") or "anonymous"
            if not _rate_limiter.is_allowed(client_key):
                return Response(response='{"success":false,"error":"Rate limit exceeded"}',
                                status=429, content_type="application/json")

            # Resolve project root for THIS chat context
            ctxid = input.get("ctxid") or input.get("context_id")
            project_root = _resolve_project_root(ctxid)
            state_file   = (project_root / ".a0proj/instructions/02-bmad-state.md") if project_root else None
            test_dir     = (project_root / ".a0proj/_bmad-output/test-artifacts")    if project_root else None

            state  = self._read_state(state_file)
            agents = self._check_agents()
            skills = self._check_skills()
            tests  = self._read_tests(test_dir)

            return {
                "success":        True,
                "generated":      datetime.now().strftime("%Y-%m-%d %H:%M"),
                "project":        str(project_root) if project_root else None,
                "state":          state,
                "agents":         agents,
                "skills":         skills,
                "tests":          tests,
                "recommendation": self._recommend(state, agents, skills, tests),
            }
        except Exception as e:
            _log.error("BMAD status read failed: %s", e, exc_info=True)
            return {"success": False, "error": "Internal error reading BMAD status"}

    def _read_state(self, state_file: Path | None):
        if state_file is None or not state_file.exists():
            return {"phase": "not_initialized", "artifact": "none", "issues": []}
        return read_state(state_file)

    def _check_agents(self):
        healthy_names, broken_tuples = check_agents(AGENTS_DIR)
        healthy = [{"name": n, "display": AGENT_NAMES.get(n, n)} for n in healthy_names]
        broken  = [{"name": n, "display": AGENT_NAMES.get(n, n), "missing": mf}
                   for n, mf in broken_tuples]
        return {"healthy": healthy, "broken": broken, "total": len(healthy) + len(broken)}

    def _check_skills(self):
        ok, broken = check_modules(SKILLS_DIR)
        return {"ok": ok, "broken": broken, "total": len(SKILL_NAMES)}

    def _read_tests(self, test_dir: Path | None):
        if test_dir is None or not test_dir.exists():
            return {"status": "no_dir"}
        passed, total, mtime = read_tests(test_dir)
        if passed is None and mtime is None:
            return {"status": "no_report"}
        if passed is None:
            return {"status": "no_match", "verified": mtime}
        return {"status": "ok", "passed": int(passed), "total": int(total), "verified": mtime,
                "failing": int(total) - int(passed)}

    def _recommend(self, state: dict, agents: dict, skills: dict, tests: dict):
        issues = []
        if skills["broken"]:
            issues.append({"sev":"blocker","what":str(len(skills["broken"]))+" module(s) missing",
                "fix":"Verify BMAD plugin is installed and enabled"})
        if agents["broken"]:
            issues.append({"sev":"warn","what":str(len(agents["broken"]))+" agent(s) unhealthy",
                "fix":"Restore missing prompt files - see Agent Health section"})
        if tests.get("failing",0) > 0:
            issues.append({"sev":"warn","what":str(tests["failing"])+" test(s) failing",
                "fix":"Review test-artifacts/behavioral-test-report*.md"})
        if state["issues"]:
            issues.append({"sev":"open","what":str(len(state["issues"]))+" open ARCH/DEFECT item(s)",
                "fix":"Address in next sprint"})
        phase     = state["phase"].lower()
        phase_key = "ready"
        for k in PHASE_ACTIONS:
            if k not in ("ready","unknown","not_initialized") and k in phase:
                phase_key = k
                break
        if phase in ("unknown","not_initialized"):
            phase_key = "not_initialized"
        label, action = PHASE_ACTIONS[phase_key]
        return {"issues":issues,"label":label,"action":action}
