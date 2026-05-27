# BMAD State & Artifact Delivery Fixes — TODO

**Source of truth:** `SPEC.md` (1,087 lines)
**Branch:** `develop` → `main` on `/ship`
**Total tasks:** 13 (T0–T12)

---

## Phase 1: Pre-flight

---

### T0: Pre-flight Verification
- [x] **T0.1** Grep all 8 Fix A target files for `cat >.*STATEEOF` — confirm bug pattern present at expected lines
- [x] **T0.2** Grep Fix B1 target file `prompts/bmad-agent-shared.md` — confirm line 187 contains `Update state after phase transitions`
- [x] **T0.3** Grep Fix C1 target file `agents/bmad-master/prompts/agent.system.main.communication_additions.md` — confirm line 161 contains `Everything else → mandatory routing lookup`
- [x] **T0.4** Run existing test suite baseline — confirm all tests pass before changes

**Verification:**
~~~bash
cd /a0/usr/projects/a0_bmad_method
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md
python -m pytest tests/ -v --tb=short 2>&1 | tail -5
~~~

**Dependencies:** None
**Scope:** XS (read-only checks)

---

## Phase 2: Fix A — A-only Files (4 tasks, parallel after T0)

---

### T1: Fix A4 — step-14-complete.md (UX Design)
- [x] **T1.1** Read `skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md` lines 165–190 to confirm exact BEFORE text
- [x] **T1.2** Replace `## Workflow Completion — State Write (MANDATORY)` section (lines 171–185) with `text_editor:patch` instructions: Phase=`3-solutioning`, Artifact=`ux-design-specification.md`, Persona=`BMad Master (Orchestrator)`
- [x] **T1.3** Verify no `cat >` heredoc remains; verify `text_editor:patch` instructions present; verify correct Phase/Artifact/Persona values

**Acceptance:**
- No `cat >` heredoc in file
- Has `text_editor:patch` with `patch_text` instructions
- Phase: `3-solutioning`, Active Artifact: `ux-design-specification.md`, Persona: `BMad Master (Orchestrator)`

**Verification:**
~~~bash
grep -c 'cat >.*STATEEOF' skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md  # → 0
grep -c 'text_editor:patch' skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md  # → ≥1
grep '3-solutioning' skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md | head -1
grep 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md
~~~

**Dependencies:** T0
**Scope:** XS (1 file, mechanical replacement)

---

### T2: Fix A5 — sprint-planning/checklist.md
- [x] **T2.1** Read `skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md` lines 28–55 to confirm exact BEFORE text
- [x] **T2.2** Replace `## Workflow Completion — State Write (MANDATORY)` section (lines 34–48) with `text_editor:patch` instructions: Phase=`4-implementation`, Artifact=`sprint-status.yaml`, Persona=`BMad Master (Orchestrator)`
- [x] **T2.3** Verify no `cat >` heredoc remains; verify `text_editor:patch` instructions present; verify correct Phase/Artifact/Persona values

**Acceptance:**
- No `cat >` heredoc in file
- Has `text_editor:patch` with `patch_text` instructions
- Phase: `4-implementation`, Active Artifact: `sprint-status.yaml`, Persona: `BMad Master (Orchestrator)`

**Verification:**
~~~bash
grep -c 'cat >.*STATEEOF' skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md  # → 0
grep -c 'text_editor:patch' skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md  # → ≥1
grep 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md
~~~

**Dependencies:** T0
**Scope:** XS (1 file, mechanical replacement)

---

### T3: Fix A6 — dev-story/checklist.md
- [x] **T3.1** Read `skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md` lines 74–100 to confirm exact BEFORE text
- [x] **T3.2** Replace `## Workflow Completion — State Write (MANDATORY)` section (lines 80–94) with `text_editor:patch` instructions: Phase=`4-implementation`, Artifact=`story.md`, Persona=`BMad Master (Orchestrator)`
- [x] **T3.3** Verify no `cat >` heredoc remains; verify `text_editor:patch` instructions present; verify correct Phase/Artifact/Persona values

**Acceptance:**
- No `cat >` heredoc in file
- Has `text_editor:patch` with `patch_text` instructions
- Phase: `4-implementation`, Active Artifact: `story.md`, Persona: `BMad Master (Orchestrator)`

**Verification:**
~~~bash
grep -c 'cat >.*STATEEOF' skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md  # → 0
grep -c 'text_editor:patch' skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md  # → ≥1
grep 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md
~~~

**Dependencies:** T0
**Scope:** XS (1 file, mechanical replacement)

---

### T4: Fix A8 — quick-spec/workflow.md
- [x] **T4.1** Read `skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md` lines 73–100 to confirm exact BEFORE text
- [x] **T4.2** Replace `## Workflow Completion — State Write (MANDATORY)` section (lines 79–93) with `text_editor:patch` instructions: Phase=`4-implementation`, Artifact=`quick-spec.md`, Persona=`BMad Master (Orchestrator)`
- [x] **T4.3** Verify no `cat >` heredoc remains; verify `text_editor:patch` instructions present; verify correct Phase/Artifact/Persona values

**Acceptance:**
- No `cat >` heredoc in file
- Has `text_editor:patch` with `patch_text` instructions
- Phase: `4-implementation`, Active Artifact: `quick-spec.md`, Persona: `BMad Master (Orchestrator)`

**Verification:**
~~~bash
grep -c 'cat >.*STATEEOF' skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md  # → 0
grep -c 'text_editor:patch' skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md  # → ≥1
grep 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md
~~~

**Dependencies:** T0
**Scope:** XS (1 file, mechanical replacement)

---

## Phase 2: Fix A+B — Dual-change Files (4 tasks, parallel after T0)

---

### T5: Fix A1+B2 — step-06-complete.md (Product Brief)
- [x] **T5.1** Read `skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md` lines 155–185 to confirm exact BEFORE text for both Fix A and Fix B
- [x] **T5.2** Replace `## Workflow Completion — State Write (MANDATORY)` section (lines 162–176) with `text_editor:patch` instructions: Phase=`2-planning`, Artifact=`product-brief.md`, Persona=`BMad Master (Orchestrator)` (Fix A1)
- [x] **T5.3** Prefix celebration text at line 180 with `**Display to user (do NOT write to any file):**` (Fix B2)
- [x] **T5.4** Verify no `cat >` heredoc; verify `text_editor:patch` instructions; verify display-only prefix; verify correct Phase/Artifact/Persona

**Acceptance:**
- No `cat >` heredoc in file
- Has `text_editor:patch` with `patch_text` instructions
- Phase: `2-planning`, Active Artifact: `product-brief.md`, Persona: `BMad Master (Orchestrator)`
- Celebration line has `**Display to user (do NOT write to any file):**` prefix

**Verification:**
~~~bash
grep -c 'cat >.*STATEEOF' skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md  # → 0
grep -c 'text_editor:patch' skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md  # → ≥1
grep 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md
grep 'Display to user (do NOT write to any file)' skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md
~~~

**Dependencies:** T0
**Scope:** XS (1 file, two targeted edits)

---

### T6: Fix A2+B3 — step-12-complete.md (PRD)
- [x] **T6.1** Read `skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md` lines 117–147 to confirm exact BEFORE text for both Fix A and Fix B
- [x] **T6.2** Replace `## Workflow Completion — State Write (MANDATORY)` section (lines 124–138) with `text_editor:patch` instructions: Phase=`2-planning`, Artifact=`prd.md`, Persona=`BMad Master (Orchestrator)` (Fix A2)
- [x] **T6.3** Prefix celebration text at line 142 with `**Display to user (do NOT write to any file):**` (Fix B3)
- [x] **T6.4** Verify no `cat >` heredoc; verify `text_editor:patch` instructions; verify display-only prefix; verify correct Phase/Artifact/Persona

**Acceptance:**
- No `cat >` heredoc in file
- Has `text_editor:patch` with `patch_text` instructions
- Phase: `2-planning`, Active Artifact: `prd.md`, Persona: `BMad Master (Orchestrator)`
- Celebration line has `**Display to user (do NOT write to any file):**` prefix

**Verification:**
~~~bash
grep -c 'cat >.*STATEEOF' skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md  # → 0
grep -c 'text_editor:patch' skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md  # → ≥1
grep 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md
grep 'Display to user (do NOT write to any file)' skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md
~~~

**Dependencies:** T0
**Scope:** XS (1 file, two targeted edits)

---

### T7: Fix A3+B4 — step-08-complete.md (Architecture)
- [x] **T7.1** Read `skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md` lines 69–100 to confirm exact BEFORE text for both Fix A and Fix B
- [x] **T7.2** Replace `## Workflow Completion — State Write (MANDATORY)` section (lines 76–90) with `text_editor:patch` instructions: Phase=`3-solutioning`, Artifact=`architecture.md`, Persona=`BMad Master (Orchestrator)` (Fix A3)
- [x] **T7.3** Prefix announcement text at line 94 with `**Display to user (do NOT write to any file):**` (Fix B4)
- [x] **T7.4** Verify no `cat >` heredoc; verify `text_editor:patch` instructions; verify display-only prefix; verify correct Phase/Artifact/Persona

**Acceptance:**
- No `cat >` heredoc in file
- Has `text_editor:patch` with `patch_text` instructions
- Phase: `3-solutioning`, Active Artifact: `architecture.md`, Persona: `BMad Master (Orchestrator)`
- Announcement line has `**Display to user (do NOT write to any file):**` prefix

**Verification:**
~~~bash
grep -c 'cat >.*STATEEOF' skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md  # → 0
grep -c 'text_editor:patch' skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md  # → ≥1
grep 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md
grep 'Display to user (do NOT write to any file)' skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md
~~~

**Dependencies:** T0
**Scope:** XS (1 file, two targeted edits)

---

### T8: Fix A7+B5 — step-04-final-validation.md (Epics & Stories)
- [x] **T8.1** Read `skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md` lines 155–185 to confirm exact BEFORE text for both Fix A and Fix B
- [x] **T8.2** Replace `## Workflow Completion — State Write (MANDATORY)` section (lines 162–176) with `text_editor:patch` instructions: Phase=`4-implementation`, Artifact=`epics.md`, Persona=`BMad Master (Orchestrator)` (Fix A7)
- [x] **T8.3** Prefix announcement text at line 180 with `**Display to user (do NOT write to any file):**` (Fix B5)
- [x] **T8.4** Verify no `cat >` heredoc; verify `text_editor:patch` instructions; verify display-only prefix; verify correct Phase/Artifact/Persona

**Acceptance:**
- No `cat >` heredoc in file
- Has `text_editor:patch` with `patch_text` instructions
- Phase: `4-implementation`, Active Artifact: `epics.md`, Persona: `BMad Master (Orchestrator)`
- Announcement line has `**Display to user (do NOT write to any file):**` prefix

**Verification:**
~~~bash
grep -c 'cat >.*STATEEOF' skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md  # → 0
grep -c 'text_editor:patch' skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md  # → ≥1
grep 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md
grep 'Display to user (do NOT write to any file)' skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md
~~~

**Dependencies:** T0
**Scope:** XS (1 file, two targeted edits)

---

### Checkpoint A: Fix A Complete
~~~bash
cd /a0/usr/projects/a0_bmad_method
# Zero cat> heredocs across all 8 files
grep -rl 'cat >.*STATEEOF' skills/bmad-bmm/workflows/ && echo 'FAIL: heredocs remain' || echo 'OK: all heredocs removed'
# Zero $(date literals
grep -r '\$\(date' skills/bmad-bmm/workflows/ --include='*.md' && echo 'FAIL: $(date) literals remain' || echo 'OK: no $(date) literals'
# All 8 files have text_editor:patch
for f in \
  skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md \
  skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md \
  skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md \
  skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md \
  skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md \
  skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md \
  skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md \
  skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md; do
  grep -q 'text_editor:patch' "$f" && echo "OK: $f" || echo "FAIL: $f"
done
# All 8 files reset persona
grep -rl 'BMad Master (Orchestrator)' skills/bmad-bmm/workflows/ | wc -l  # → 8
~~~

---

### T9: Fix B1 — bmad-agent-shared.md (Global Celebration Guard)
- [x] **T9.1** Read `prompts/bmad-agent-shared.md` lines 180–190 to confirm line 187 contains `Update state after phase transitions`
- [x] **T9.2** Insert new line after line 187: `- **Never write celebration/summary files**: When a workflow announces completion or says "Congratulations", DISPLAY the message to the user in your response text. Do NOT create any summary, celebration, or announcement files on disk. The only file writes allowed are the explicit artifact paths and state updates specified in the workflow.`
- [x] **T9.3** Verify new line present after the `Update state after phase transitions` line

**Acceptance:**
- `prompts/bmad-agent-shared.md` contains `**Never write celebration/summary files**` rule
- Rule appears after the `Update state after phase transitions` line in "File and Artifact Handling" section

**Verification:**
~~~bash
grep -A1 'Update state after phase transitions' prompts/bmad-agent-shared.md | grep 'Never write celebration'
grep -c 'Never write celebration/summary files' prompts/bmad-agent-shared.md  # → 1
~~~

**Dependencies:** T0
**Scope:** XS (1 file, 1 line insertion)

---

### Checkpoint B: Fix B Complete
~~~bash
# Global guard present
grep -c 'Never write celebration/summary files' prompts/bmad-agent-shared.md  # → 1
# All 4 display-only prefixes present
grep -c 'Display to user (do NOT write to any file)' skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md  # → 1
grep -c 'Display to user (do NOT write to any file)' skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md  # → 1
grep -c 'Display to user (do NOT write to any file)' skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md  # → 1
grep -c 'Display to user (do NOT write to any file)' skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md  # → 1
~~~

---

## Phase 3: Fix C (after Fix A)

---

### T10: Fix C1 — communication_additions.md (Post-Delegation Verification)
- [x] **T10.1** Read `agents/bmad-master/prompts/agent.system.main.communication_additions.md` lines 150–165 to confirm line 161 contains `Everything else → mandatory routing lookup → delegate to correct specialist profile.`
- [x] **T10.2** Insert after line 161 the `## Post-Delegation Verification (MANDATORY)` section with 3 steps:
  1. Verify state integrity: Read `02-bmad-state.md`, confirm `- Persona: BMad Master (Orchestrator)` present. If corrupted, fix immediately.
  2. Verify artifact exists: Check declared artifact file exists at configured output path and is non-empty.
  3. Report results to user: Confirm what was created and where, or report any verification failures.
- [x] **T10.3** Verify section header and all 3 verification steps present

**Acceptance:**
- `communication_additions.md` contains `## Post-Delegation Verification (MANDATORY)` section header
- Section has all 3 steps: state integrity, artifact exists, report results
- Section appears after `Everything else → mandatory routing lookup` line

**Verification:**
~~~bash
grep -c 'Post-Delegation Verification (MANDATORY)' agents/bmad-master/prompts/agent.system.main.communication_additions.md  # → 1
grep -c 'Verify state integrity' agents/bmad-master/prompts/agent.system.main.communication_additions.md  # → 1
grep -c 'Verify artifact exists' agents/bmad-master/prompts/agent.system.main.communication_additions.md  # → 1
grep -c 'Report results to user' agents/bmad-master/prompts/agent.system.main.communication_additions.md  # → 1
~~~

**Dependencies:** T1–T8 (Fix A must be complete — verification targets patched files)
**Scope:** XS (1 file, 1 section insertion)

---

### Checkpoint C: Fix C Complete
~~~bash
grep -c 'Post-Delegation Verification (MANDATORY)' agents/bmad-master/prompts/agent.system.main.communication_additions.md  # → 1
~~~

---

## Phase 4: Regression + Commit

---

### T11: Regression Tests
- [x] **T11.1** Inverse pre-flight: grep all 8 files — zero `cat >` heredocs remain
- [x] **T11.2** Inverse pre-flight: grep all 8 files — zero `$(date` literals remain
- [x] **T11.3** Full pytest suite passes
- [x] **T11.4** Manual verification checklist from SPEC.md §Manual Verification Checklist
- [x] **T11.5** `git diff --stat` shows exactly 10 files changed

**Acceptance:**
- Zero `cat >` heredocs in any of 8 target files
- Zero `$(date` literal strings in any workflow file
- All existing pytest tests pass without modification
- `bmad_status_core.py` regex patterns still match
- `git diff --stat` shows exactly 10 files

**Verification:**
~~~bash
cd /a0/usr/projects/a0_bmad_method
# Inverse pre-flight
grep -rl 'cat >.*STATEEOF' skills/bmad-bmm/workflows/ && echo 'FAIL' || echo 'OK: no heredocs'
grep -r '\$\(date' skills/bmad-bmm/workflows/ --include='*.md' && echo 'FAIL' || echo 'OK: no date literals'
# Full test suite
python -m pytest tests/ -v --tb=short 2>&1 | tail -10
# File count
git diff --stat | tail -1
~~~

**Dependencies:** T1–T10 (all fixes applied)
**Scope:** S (verification only, no code changes)

---

### T12: Git Commits
- [x] **T12.1** `git add` all Fix A files (8 files), commit: `fix: replace cat> heredocs with text_editor:patch (Bug 1, 3, Bonus)`
- [x] **T12.2** `git add` all Fix B files (5 changes in 5 files), commit: `fix: add celebration message display-only guards (Bug 2)`
- [x] **T12.3** `git add` Fix C file (1 file), commit: `fix: add post-delegation verification to BMad Master (Bug 4)`
- [x] **T12.4** Verify `git log --oneline -3` shows 3 new commits

**Acceptance:**
- 3 commits, one per fix layer (A, B, C)
- Each commit message references the bugs it fixes
- `git log --oneline -3` shows the 3 new commits

**Verification:**
~~~bash
cd /a0/usr/projects/a0_bmad_method
git log --oneline -3
git diff --stat HEAD~3  # should show 10 files total
~~~

**Dependencies:** T11 (tests pass)
**Scope:** XS (git operations only)

---

## Summary

| Task | Fix | File(s) | Scope | Depends on |
|------|-----|---------|-------|------------|
| T0 | Pre-flight | — | XS | — |
| T1 | A4 | step-14-complete.md | XS | T0 |
| T2 | A5 | sprint-planning/checklist.md | XS | T0 |
| T3 | A6 | dev-story/checklist.md | XS | T0 |
| T4 | A8 | quick-spec/workflow.md | XS | T0 |
| T5 | A1+B2 | step-06-complete.md | XS | T0 |
| T6 | A2+B3 | step-12-complete.md | XS | T0 |
| T7 | A3+B4 | step-08-complete.md | XS | T0 |
| T8 | A7+B5 | step-04-final-validation.md | XS | T0 |
| T9 | B1 | bmad-agent-shared.md | XS | T0 |
| T10 | C1 | communication_additions.md | XS | T1–T8 |
| T11 | Regression | — | S | T1–T10 |
| T12 | Commits | — | XS | T11 |

**Total:** 13 tasks, 14 changes, 10 unique files. All XS except T11 (S).
