"""BMAD State & Artifact Delivery Fixes — grep-based regression tests.

Verifies that all 8 workflow completion files use text_editor:patch
instead of cat> heredocs, and that celebration/verification guards are present.
"""

import os
import subprocess
import pytest

PROJECT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# The 8 Fix A target files
FIX_A_FILES = [
    f"{PROJECT}/skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md",
]

# Fix B2-B5 target files (display-only prefix)
FIX_B_DISPLAY_FILES = [
    f"{PROJECT}/skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md",
    f"{PROJECT}/skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md",
]

# Fix C target file
FIX_C_FILE = f"{PROJECT}/agents/bmad-master/prompts/agent.system.main.communication_additions.md"

# Fix B1 target file
FIX_B1_FILE = f"{PROJECT}/prompts/bmad-agent-shared.md"


def _grep(pattern: str, path: str, mode: str = "basic") -> int:
    """Return grep match count for pattern in file.

    mode: 'basic' (default), 'extended' (-E), or 'fixed' (-F)
    """
    flags = {"basic": [], "extended": ["-E"], "fixed": ["-F"]}
    result = subprocess.run(
        ["grep", "-c"] + flags.get(mode, []) + [pattern, path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return 0
    return int(result.stdout.strip())


def _grep_extended(pattern, path):
    return _grep(pattern, path, mode="extended")


def _grep_fixed(pattern, path):
    return _grep(pattern, path, mode="fixed")


# ============================================================
# Fix A: No cat> heredocs, text_editor:patch present, correct values
# ============================================================

@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_no_cat_heredocs(filepath):
    """No cat > STATEEOF heredocs remain in any workflow file."""
    assert _grep_fixed("cat >", filepath) == 0 and _grep_fixed("STATEEOF", filepath) == 0, \
        f"cat> heredoc still present in {filepath}"


@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_text_editor_patch_present(filepath):
    """text_editor:patch instructions present in all 8 files."""
    assert _grep_fixed("text_editor:patch", filepath) >= 1, f"text_editor:patch missing in {filepath}"


@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_persona_bmad_master(filepath):
    """Persona always set to BMad Master (Orchestrator) in all 8 files."""
    assert _grep_fixed("BMad Master (Orchestrator)", filepath) >= 1, \
        f"BMad Master persona missing in {filepath}"


@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_state_update_not_write(filepath):
    """Section header says 'State Update' not 'State Write'."""
    assert _grep_fixed("State Update (MANDATORY)", filepath) >= 1, \
        f"State Update header missing in {filepath}"
    assert _grep_fixed("State Write (MANDATORY)", filepath) == 0, \
        f"Old 'State Write' header still in {filepath}"


# Per-file Phase/Artifact checks using extended regex for .*

def test_fix_a1_step06_phase_artifact():
    f = FIX_A_FILES[0]
    assert _grep_extended("Phase.*2-planning", f) >= 1
    assert _grep_extended("Active Artifact.*product-brief.md", f) >= 1

def test_fix_a2_step12_phase_artifact():
    f = FIX_A_FILES[1]
    assert _grep_extended("Phase.*2-planning", f) >= 1
    assert _grep_extended("Active Artifact.*prd.md", f) >= 1

def test_fix_a3_step08_phase_artifact():
    f = FIX_A_FILES[2]
    assert _grep_extended("Phase.*3-solutioning", f) >= 1
    assert _grep_extended("Active Artifact.*architecture.md", f) >= 1

def test_fix_a4_step14_phase_artifact():
    f = FIX_A_FILES[3]
    assert _grep_extended("Phase.*3-solutioning", f) >= 1
    assert _grep_extended("Active Artifact.*ux-design-specification.md", f) >= 1

def test_fix_a5_sprint_planning_phase_artifact():
    f = FIX_A_FILES[4]
    assert _grep_extended("Phase.*4-implementation", f) >= 1
    assert _grep_extended("Active Artifact.*sprint-status.yaml", f) >= 1

def test_fix_a6_dev_story_phase_artifact():
    f = FIX_A_FILES[5]
    assert _grep_extended("Phase.*4-implementation", f) >= 1
    assert _grep_extended("Active Artifact.*story.md", f) >= 1

def test_fix_a7_step04_phase_artifact():
    f = FIX_A_FILES[6]
    assert _grep_extended("Phase.*4-implementation", f) >= 1
    assert _grep_extended("Active Artifact.*epics.md", f) >= 1

def test_fix_a8_quick_spec_phase_artifact():
    f = FIX_A_FILES[7]
    assert _grep_extended("Phase.*4-implementation", f) >= 1
    assert _grep_extended("Active Artifact.*quick-spec.md", f) >= 1


# ============================================================
# Fix A: No $(date literals
# ============================================================

@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_no_date_literals(filepath):
    """No $(date literals remain in any workflow file."""
    assert _grep_fixed("$(date", filepath) == 0, f"$(date literal still present in {filepath}"


# ============================================================
# Fix B: Celebration guards
# ============================================================

def test_fix_b1_global_celebration_guard():
    """bmad-agent-shared.md contains the global celebration guard rule."""
    assert _grep_fixed("Never write celebration/summary files", FIX_B1_FILE) >= 1


@pytest.mark.parametrize("filepath", FIX_B_DISPLAY_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-04-final-validation", "step-14-complete",
])
def test_fix_b2_b5_display_only_prefix(filepath):
    """Display-only prefix present in 4 celebration/announcement files."""
    assert _grep_fixed("Display to user (do NOT write to any file)", filepath) >= 1


# ============================================================
# Fix C: Post-delegation verification
# ============================================================

def test_fix_c1_section_header():
    """communication_additions.md contains Post-Delegation Verification section."""
    assert _grep_fixed("Post-Delegation Verification (MANDATORY)", FIX_C_FILE) >= 1


def test_fix_c1_verify_state_integrity():
    assert _grep_fixed("Verify state integrity", FIX_C_FILE) >= 1

def test_fix_c1_verify_artifact_exists():
    assert _grep_fixed("Verify artifact exists", FIX_C_FILE) >= 1

def test_fix_c1_report_results():
    assert _grep_fixed("Report results to user", FIX_C_FILE) >= 1


# ============================================================
# Edge Case: Structural Integrity (Fix A)
# ============================================================

@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_begin_end_patch_pairs(filepath):
    """Every file with text_editor:patch must have matching Begin Patch and End Patch."""
    assert _grep_fixed("Begin Patch", filepath) >= 1, f"Missing Begin Patch in {filepath}"
    assert _grep_fixed("End Patch", filepath) >= 1, f"Missing End Patch in {filepath}"


@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_always_reset_wording(filepath):
    """Every file must instruct 'ALWAYS reset' persona to BMad Master."""
    assert _grep_fixed("ALWAYS reset", filepath) >= 1, f"Missing 'ALWAYS reset' in {filepath}"


@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_critical_preserve_instruction(filepath):
    """Every file must have CRITICAL preserve/NEVER overwrite instruction."""
    has_critical = _grep_fixed("CRITICAL", filepath) >= 1 and _grep_fixed("Preserve", filepath) >= 1
    has_never = _grep_fixed("NEVER overwrite", filepath) >= 1
    assert has_critical or has_never, f"Missing CRITICAL Preserve instruction in {filepath}"


@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_no_partial_fix_cat_and_patch_coexist(filepath):
    """No file should have BOTH cat> heredoc AND text_editor:patch (partial fix)."""
    has_cat = _grep_fixed("cat >", filepath) >= 1
    has_patch = _grep_fixed("text_editor:patch", filepath) >= 1
    assert not (has_cat and has_patch), f"Partial fix detected in {filepath}: both cat> and text_editor:patch present"


@pytest.mark.parametrize("filepath", FIX_A_FILES, ids=[
    "step-06-complete", "step-12-complete", "step-08-complete", "step-14-complete",
    "sprint-planning", "dev-story", "step-04-final-validation", "quick-spec",
])
def test_fix_a_patch_example_has_all_required_fields(filepath):
    """Example patch in each file must include Phase, Active Artifact, and Persona fields."""
    content = open(filepath).read()
    # Find the example patch section
    patch_start = content.find("*** Begin Patch")
    patch_end = content.find("*** End Patch")
    assert patch_start > 0, f"No Begin Patch found in {filepath}"
    assert patch_end > patch_start, f"No End Patch after Begin Patch in {filepath}"
    patch_block = content[patch_start:patch_end]
    assert "- Phase" in patch_block, f"Example patch missing Phase field in {filepath}"
    assert "- Active Artifact" in patch_block, f"Example patch missing Active Artifact field in {filepath}"
    assert "- Persona" in patch_block, f"Example patch missing Persona field in {filepath}"


# ============================================================
# Edge Case: Celebration Guard Cross-Validation (Fix B)
# ============================================================

# Step-14 has celebration text but was NOT in FIX_B_DISPLAY_FILES.
# This test proves the bug exists and needs fixing.
FIX_B_MISSING_GUARD_FILE = (
    f"{PROJECT}/skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md"
)


def test_fix_b_step14_has_celebration_text():
    """Prove step-14 has celebration/announcement text (prerequisite for guard test)."""
    assert _grep_fixed("🎉", FIX_B_MISSING_GUARD_FILE) >= 1, "step-14 should have celebration emoji"
    assert _grep_fixed("Congratulations", FIX_B_MISSING_GUARD_FILE) >= 1, "step-14 should have Congratulations text"


def test_fix_b_step14_display_only_guard():
    """step-14-complete has celebration text — it MUST have the display-only guard too."""
    assert _grep_fixed("Display to user (do NOT write to any file)", FIX_B_MISSING_GUARD_FILE) >= 1, \
        "step-14-complete missing display-only guard despite having celebration text"


def test_fix_b_celebration_files_count_matches_guard_files():
    """Verify every file in FIX_B_DISPLAY_FILES has the display-only guard present."""
    for filepath in FIX_B_DISPLAY_FILES:
        assert _grep_fixed("Display to user (do NOT write to any file)", filepath) >= 1, \
            f"File {filepath} in FIX_B_DISPLAY_FILES but missing display-only guard"


# ============================================================
# Edge Case: Fix C Completeness
# ============================================================

def test_fix_c_single_verification_section():
    """Post-Delegation Verification section should appear exactly once."""
    assert _grep_fixed("Post-Delegation Verification (MANDATORY)", FIX_C_FILE) == 1, \
        "Post-Delegation Verification section should appear exactly once"


def test_fix_c_verification_steps_in_correct_order():
    """Verification steps should appear in the correct order within the section."""
    content = open(FIX_C_FILE).read()
    section_start = content.find("Post-Delegation Verification (MANDATORY)")
    assert section_start > 0, "Verification section not found"
    section = content[section_start:]
    pos_verify_state = section.find("Verify state integrity")
    pos_verify_artifact = section.find("Verify artifact exists")
    pos_report = section.find("Report results to user")
    assert pos_verify_state > 0, "Verify state integrity step not found"
    assert pos_verify_artifact > 0, "Verify artifact exists step not found"
    assert pos_report > 0, "Report results to user step not found"
    assert pos_verify_state < pos_verify_artifact < pos_report, \
        "Verification steps out of order: should be state → artifact → report"
