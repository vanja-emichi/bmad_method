# SPEC: BMAD State & Artifact Delivery Fixes

**Version:** 2.0 (State Fixes)
**Date:** 2026-05-07
**Status:** Draft — pending approval
**Branch:** `develop` → `main` on `/ship`
**Grounding:** `.a0proj/ideas/bmad-state-fixes.md`, `/a0/usr/workdir/vps-analysis/bmad-fix-plan-v2.md`, `/a0/usr/workdir/vps-analysis/bmad-consent-mode-analysis.md`

---

## Objective

Fix 4 critical bugs (+1 bonus) in the BMAD Method plugin's workflow completion steps that cause state corruption, stray files, and missing verification. All fixes are **prompt/instruction-only** — no Python code changes. The workflow step files are Markdown instructions that tell LLM agents what to do; by changing what we tell agents to do, we fix the root cause without restructuring the BMAD method.

### Background

A real-world 198-turn session (Consent Mode v2 project) revealed systematic failures at the artifact delivery layer. While BMad Master's orchestration and routing worked correctly, subordinate agents produced corrupted state files, stray summary files in the project root, and incomplete artifacts — all traced to destructive `cat >` heredoc patterns in the workflow completion step instructions.

**Evidence from session analysis:**
- Mary (Analyst) wrote a 55-line completion summary instead of her 317-line product brief → caused by celebration text being written to the artifact file
- John (PM) created a stray `Document.md` in the project root → caused by completion step writing a summary file alongside the actual artifact
- State file was completely overwritten after each workflow → `cat >` heredoc destroys all accumulated context (initiative description, completed workflows, technical investigation logs)
- Persona was set to subordinate name (e.g., `BMad Mary (Business Analyst)`) instead of `BMad Master (Orchestrator)` → breaks subsequent routing
- `$(date +%Y-%m-%d)` was written as a literal string because the heredoc delimiter was single-quoted `<< 'STATEEOF'`

### User Stories

| # | As a… | I want… | So that… |
|---|-------|---------|----------|
| 1 | BMad Master | subordinate agents to always reset persona to me after workflow completion | routing continues working after workflow returns |
| 2 | Developer using BMAD | workflow completion to preserve all accumulated state context | my initiative description, completed workflows, and technical investigation logs survive across phases |
| 3 | Developer using BMAD | dates in the state file to be actual dates | I can see when the project was last updated |
| 4 | Developer using BMAD | no stray summary/celebration files in my project root | my project directory stays clean with only real artifacts |
| 5 | BMad Master | to verify artifacts exist after subordinate returns | missing or empty artifacts are caught immediately |

### Bug Summary

| # | Bug | Root Cause | Fix Layer | Severity |
|---|-----|-----------|-----------|----------|
| 1 | Persona state corruption | `cat >` heredocs hardcode subordinate persona | Fix A | 🔴 Critical |
| 2 | Stray summary files | Celebration text lacks display-only guard | Fix B | 🔴 High |
| 3 | Full state file overwrite | `cat >` replaces entire file | Fix A | 🔴 Critical |
| 4 | No post-creation verification | No artifact validation after subordinate returns | Fix C | 🟡 Medium |
| 💰 | `$(date)` never expands | Single-quoted heredoc `<< 'STATEEOF'` | Fix A | 🟡 Bonus |

### 3-Layer Fix Approach

| Fix | What | Files | Bugs Addressed |
|-----|------|-------|---------------|
| **A** | Replace `cat >` heredocs with `text_editor:patch` instructions | 8 completion step files | 1 + 3 + Bonus |
| **B** | Add celebration message "display-only" guards | 1 shared prompt + 4 step files | 2 |
| **C** | Add post-delegation verification to BMad Master | 1 orchestration prompt | 4 |

**Total:** 14 changes across 10 unique files. 0 new files. 0 deletions.

---

## Tech Stack

| Layer | Technology | Notes |
|-------|-----------|-------|
| Content type | Markdown prompt files | Instructions that tell LLM agents what to do — NOT executable code |
| Fix mechanism | `text_editor:patch` with `patch_text` | Agent Zero's native file editing tool |
| Built-in safety | Freshness checks | Context lines must match current file content; patch rejected if stale |
| State file | `02-bmad-state.md` | YAML-like markdown with key-value fields under `## BMAD Active State` |
| Regression risk | `bmad_status_core.py` regex patterns | Must still match after fix: `_PHASE_RE`, `_ARTIFACT_RE` |
| Regression risk | `bmad-init.sh` | Creates initial state file — NOT modified |
| VCS | Git | `develop` branch → `main` on `/ship` |

### Why `text_editor:patch` instead of `sed` or `cat >`

1. **Agent Zero native** — uses the agent's own toolset, not external bash commands
2. **Built-in freshness checks** — context lines must match current content; silent corruption impossible
3. **LLM-friendly** — natural language instructions, not bash syntax
4. **Field-level** — modifies only specified lines, preserves all other content
5. **Fail-safe** — if context lines don't match, patch fails explicitly rather than silently corrupting
6. **Idempotent** — running patch twice with same context produces same result

---

## Project Structure

All paths relative to project root: `/a0/usr/projects/a0_bmad_method/`

### Target Files (10 files being modified)

```
skills/bmad-bmm/workflows/
├── 1-analysis/create-product-brief/steps/
│   └── step-06-complete.md                          ← Fix A1 + Fix B2
├── 2-plan-workflows/
│   ├── create-prd/steps-c/
│   │   └── step-12-complete.md                      ← Fix A2 + Fix B3
│   └── create-ux-design/steps/
│       └── step-14-complete.md                      ← Fix A4
├── 3-solutioning/
│   ├── create-architecture/steps/
│   │   └── step-08-complete.md                      ← Fix A3 + Fix B4
│   └── create-epics-and-stories/steps/
│       └── step-04-final-validation.md              ← Fix A7 + Fix B5
├── 4-implementation/
│   ├── dev-story/
│   │   └── checklist.md                             ← Fix A6
│   └── sprint-planning/
│       └── checklist.md                             ← Fix A5
└── bmad-quick-flow/quick-spec/
    └── workflow.md                                  ← Fix A8

prompts/
└── bmad-agent-shared.md                            ← Fix B1 (global celebration guard)

agents/bmad-master/prompts/
└── agent.system.main.communication_additions.md     ← Fix C1 (post-delegation verify)
```

### Regression-Risk Files (NOT modified, must still work)

```
helpers/bmad_status_core.py        ← regex patterns: _PHASE_RE, _ARTIFACT_RE
skills/bmad-init/scripts/bmad-init.sh  ← creates initial state file
api/_bmad_status.py                ← None-guard, uses read_state()
helpers/__init__.py                ← exports read_state
```

---

## Changes

### Change Matrix

| # | File (short) | Fix | Bugs | Lines | Type |
|---|-------------|-----|------|-------|------|
| A1 | `1-analysis/.../step-06-complete.md` | text_editor:patch state update | 1+3+💰 | 162–176 | Replace |
| A2 | `2-plan-workflows/.../step-12-complete.md` | text_editor:patch state update | 1+3+💰 | 124–138 | Replace |
| A3 | `3-solutioning/.../step-08-complete.md` | text_editor:patch state update | 1+3+💰 | 76–90 | Replace |
| A4 | `2-plan-workflows/.../step-14-complete.md` | text_editor:patch state update | 1+3+💰 | 171–185 | Replace |
| A5 | `4-implementation/.../sprint-planning/checklist.md` | text_editor:patch state update | 1+3+💰 | 34–48 | Replace |
| A6 | `4-implementation/.../dev-story/checklist.md` | text_editor:patch state update | 1+3+💰 | 80–94 | Replace |
| A7 | `3-solutioning/.../step-04-final-validation.md` | text_editor:patch state update | 1+3+💰 | 162–176 | Replace |
| A8 | `bmad-quick-flow/.../workflow.md` | text_editor:patch state update | 1+3+💰 | 79–93 | Replace |
| B1 | `prompts/bmad-agent-shared.md` | celebration guard rule | 2 | after 187 | Insert |
| B2 | `1-analysis/.../step-06-complete.md` | display-only wrap | 2 | 180 | Edit |
| B3 | `2-plan-workflows/.../step-12-complete.md` | display-only wrap | 2 | 142 | Edit |
| B4 | `3-solutioning/.../step-08-complete.md` | display-only wrap | 2 | 94 | Edit |
| B5 | `3-solutioning/.../step-04-final-validation.md` | display-only wrap | 2 | 180 | Edit |
| C1 | `agents/bmad-master/.../communication_additions.md` | post-delegation verify | 4 | after 161 | Insert |

**Total:** 14 changes across 10 unique files. No new files created. No file deletions.

---

### Fix A: State Update via text_editor:patch (8 files)

**Fixes:** Bug 1 (persona corruption) + Bug 3 (full overwrite) + Bonus (date literal)

#### Canonical BEFORE Pattern

This exact pattern appears in all 8 files (with varying Phase, Persona, and Artifact values):

```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: <PHASE>
- Persona: BMad <Subordinate> (<Role>)
- Active Artifact: <ARTIFACT>
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**Problems:**
- `cat >` overwrites entire file → destroys initiative context, completed workflows, logs
- Hardcodes subordinate persona → persona leaks into subsequent routing
- `<< 'STATEEOF'` (single-quoted) → `$(date)` never expands, written as literal string
- No freshness check → silent corruption if file structure changed

#### Canonical AFTER Pattern

All 8 files get this pattern (with per-file Phase and Artifact values):

```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `<PHASE>`
   - `Active Artifact` → `<ARTIFACT>`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: <PHASE>
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: <ARTIFACT>
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

**Per-file values:**

| Change | File | Phase | Artifact | Persona (BUG) |
|--------|------|-------|----------|---------------|
| A1 | step-06-complete.md | `2-planning` | `product-brief.md` | BMad Mary (Business Analyst) |
| A2 | step-12-complete.md | `2-planning` | `prd.md` | BMad John (Product Manager) |
| A3 | step-08-complete.md | `3-solutioning` | `architecture.md` | BMad Winston (Architect) |
| A4 | step-14-complete.md | `3-solutioning` | `ux-design-specification.md` | BMad Sally (UX Designer) |
| A5 | sprint-planning/checklist.md | `4-implementation` | `sprint-status.yaml` | BMad Bob (Scrum Master) |
| A6 | dev-story/checklist.md | `4-implementation` | `story.md` | BMad Amelia (Developer Agent) |
| A7 | step-04-final-validation.md | `4-implementation` | `epics.md` | BMad Bob (Scrum Master) |
| A8 | quick-spec/workflow.md | `4-implementation` | `quick-spec.md` | BMad Barry (Quick Flow Solo Dev) |

#### File-by-File Details

##### Change A1: step-06-complete.md (Product Brief)

**Path:** `skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md`
**Lines:** 162–176 (replace entire section)

**BEFORE:**
```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: 2-planning
- Persona: BMad Mary (Business Analyst)
- Active Artifact: product-brief.md
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**AFTER:**
```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `2-planning`
   - `Active Artifact` → `product-brief.md`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: 2-planning
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: product-brief.md
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

---

##### Change A2: step-12-complete.md (PRD)

**Path:** `skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md`
**Lines:** 124–138 (replace entire section)

**BEFORE:**
```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: 2-planning
- Persona: BMad John (Product Manager)
- Active Artifact: prd.md
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**AFTER:**
```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `2-planning`
   - `Active Artifact` → `prd.md`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: 2-planning
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: prd.md
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

---

##### Change A3: step-08-complete.md (Architecture)

**Path:** `skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md`
**Lines:** 76–90 (replace entire section)

**BEFORE:**
```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: 3-solutioning
- Persona: BMad Winston (Architect)
- Active Artifact: architecture.md
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**AFTER:**
```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `3-solutioning`
   - `Active Artifact` → `architecture.md`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: 3-solutioning
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: architecture.md
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

---

##### Change A4: step-14-complete.md (UX Design)

**Path:** `skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md`
**Lines:** 171–185 (replace entire section)

**BEFORE:**
```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: 3-solutioning
- Persona: BMad Sally (UX Designer)
- Active Artifact: ux-design-specification.md
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**AFTER:**
```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `3-solutioning`
   - `Active Artifact` → `ux-design-specification.md`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: 3-solutioning
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: ux-design-specification.md
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

---

##### Change A5: sprint-planning/checklist.md

**Path:** `skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md`
**Lines:** 34–48 (replace entire section)

**BEFORE:**
```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: 4-implementation
- Persona: BMad Bob (Scrum Master)
- Active Artifact: sprint-status.yaml
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**AFTER:**
```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `4-implementation`
   - `Active Artifact` → `sprint-status.yaml`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: 4-implementation
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: sprint-status.yaml
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

---

##### Change A6: dev-story/checklist.md

**Path:** `skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md`
**Lines:** 80–94 (replace entire section)

**BEFORE:**
```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: 4-implementation
- Persona: BMad Amelia (Developer Agent)
- Active Artifact: story.md
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**AFTER:**
```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `4-implementation`
   - `Active Artifact` → `story.md`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: 4-implementation
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: story.md
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

---

##### Change A7: step-04-final-validation.md (Epics & Stories)

**Path:** `skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md`
**Lines:** 162–176 (replace entire section)

**BEFORE:**
```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: 4-implementation
- Persona: BMad Bob (Scrum Master)
- Active Artifact: epics.md
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**AFTER:**
```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `4-implementation`
   - `Active Artifact` → `epics.md`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: 4-implementation
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: epics.md
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

---

##### Change A8: quick-spec/workflow.md

**Path:** `skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md`
**Lines:** 79–93 (replace entire section)

**BEFORE:**
```markdown
## Workflow Completion — State Write (MANDATORY)

Before returning control to the user, write the updated project state using `code_execution_tool` terminal:

~~~bash
STATE_FILE="{project-root}/instructions/02-bmad-state.md"
cat > "$STATE_FILE" << 'STATEEOF'
## BMAD Active State
- Phase: 4-implementation
- Persona: BMad Barry (Quick Flow Solo Dev)
- Active Artifact: quick-spec.md
- Last Updated: $(date +%Y-%m-%d)
STATEEOF
echo "State written: $STATE_FILE"
~~~
```

**AFTER:**
```markdown
## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `4-implementation`
   - `Active Artifact` → `quick-spec.md`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date
3. **CRITICAL:** Preserve ALL other content — initiative context, completed workflows, technical investigation log, issues, notes, tables. NEVER overwrite the entire file.

**Example patch:**
~~~
*** Begin Patch
*** Update File: {project-root}/instructions/02-bmad-state.md
@@ - Phase:
-- Phase: <current value>
+- Phase: 4-implementation
@@ - Active Artifact:
-- Active Artifact: <current value>
+- Active Artifact: quick-spec.md
@@ - Persona:
-- Persona: <current value>
+- Persona: BMad Master (Orchestrator)
@@ - Last Updated:
-- Last Updated: <current value>
+- Last Updated: <today>
*** End Patch
~~~
```

---

### Fix B: Celebration Message Guard (5 additions)

**Fixes:** Bug 2 (stray summary files)

Two-layer defense:
1. **Global rule** in shared agent prompt — prevents ALL agents from writing celebration files
2. **Per-file instruction** — wraps celebration text in explicit display-only directive

#### Change B1: bmad-agent-shared.md — Add Global Rule

**Path:** `prompts/bmad-agent-shared.md`
**Action:** Insert after line 187 (end of "File and Artifact Handling" section)

**BEFORE (lines 183–187):**
```markdown
- **Save artifacts to skill-defined paths**: The loaded skill specifies where each deliverable lives — follow it exactly
- **Use config aliases**: Resolve `{planning_artifacts}`, `{implementation_artifacts}`, `{project_root}`, and other aliases from `01-bmad-config.md` to absolute paths before writing
- **Never use relative paths**: Always construct absolute paths; relative paths break when the working directory changes
- **Include rather than rewrite**: When referencing long file content in a response, use `§§include(/absolute/path/to/file)` instead of copying the text inline
- **Update state after phase transitions**: After completing a deliverable that advances the project phase, update `02-bmad-state.md` to reflect the new phase, active artifact, and any decisions made
```

**AFTER:**
```markdown
- **Save artifacts to skill-defined paths**: The loaded skill specifies where each deliverable lives — follow it exactly
- **Use config aliases**: Resolve `{planning_artifacts}`, `{implementation_artifacts}`, `{project_root}`, and other aliases from `01-bmad-config.md` to absolute paths before writing
- **Never use relative paths**: Always construct absolute paths; relative paths break when the working directory changes
- **Include rather than rewrite**: When referencing long file content in a response, use `§§include(/absolute/path/to/file)` instead of copying the text inline
- **Update state after phase transitions**: After completing a deliverable that advances the project phase, update `02-bmad-state.md` to reflect the new phase, active artifact, and any decisions made
- **Never write celebration/summary files**: When a workflow announces completion or says "Congratulations", DISPLAY the message to the user in your response text. Do NOT create any summary, celebration, or announcement files on disk. The only file writes allowed are the explicit artifact paths and state updates specified in the workflow.
```

**Why:** Global rule applies to ALL agents loading the shared prompt, not just the 4 affected workflow files. Prevents the pattern where agents create `Document.md` or `Product Brief Complete_ User.md` in the project root.

---

#### Change B2: step-06-complete.md — Wrap Celebration

**Path:** `skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md`
**Line:** 180 (edit)

**BEFORE:**
```markdown
**Congratulations on completing the Product Brief for {{project_name}}!** 🎉
```

**AFTER:**
```markdown
**Display to user (do NOT write to any file):** Congratulations on completing the Product Brief for {{project_name}}! 🎉
```

---

#### Change B3: step-12-complete.md — Wrap Celebration

**Path:** `skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md`
**Line:** 142 (edit)

**BEFORE:**
```markdown
**Congratulations on completing the Product Requirements Document for {{project_name}}!** 🎉
```

**AFTER:**
```markdown
**Display to user (do NOT write to any file):** Congratulations on completing the Product Requirements Document for {{project_name}}! 🎉
```

---

#### Change B4: step-08-complete.md — Wrap Announcement

**Path:** `skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md`
**Line:** 94 (edit)

**BEFORE:**
```markdown
The architecture will serve as the single source of truth for all technical decisions, ensuring consistent implementation across the entire project development lifecycle.
```

**AFTER:**
```markdown
**Display to user (do NOT write to any file):** The architecture will serve as the single source of truth for all technical decisions, ensuring consistent implementation across the entire project development lifecycle.
```

---

#### Change B5: step-04-final-validation.md — Wrap Announcement

**Path:** `skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md`
**Line:** 180 (edit)

**BEFORE:**
```markdown
Upon Completion of task output: offer to answer any questions about the Epics and Stories.
```

**AFTER:**
```markdown
**Display to user (do NOT write to any file):** Offer to answer any questions about the Epics and Stories.
```

---

### Fix C: BMad Master Post-Delegation Verification (1 addition)

**Fixes:** Bug 4 (no post-creation verification)

#### Change C1: communication_additions.md — Add Post-Delegation Verification

**Path:** `agents/bmad-master/prompts/agent.system.main.communication_additions.md`
**Action:** Insert after line 161 (after "Everything else → mandatory routing lookup → delegate to correct specialist profile.")

**BEFORE (lines 153–161):**
```markdown
**The only things BMad Master does directly:**
- Display menus
- Read manifests (LT/LW)
- Answer general BMAD knowledge questions (CH)
- Orchestrate Party Mode (PM)
- Read project state and config files
- Update `02-bmad-state.md` after phase transitions

**Everything else → mandatory routing lookup → delegate to correct specialist profile.**
```

**AFTER:**
```markdown
**The only things BMad Master does directly:**
- Display menus
- Read manifests (LT/LW)
- Answer general BMAD knowledge questions (CH)
- Orchestrate Party Mode (PM)
- Read project state and config files
- Update `02-bmad-state.md` after phase transitions

**Everything else → mandatory routing lookup → delegate to correct specialist profile.**

## Post-Delegation Verification (MANDATORY)

After a subordinate completes a workflow and returns control:
1. **Verify state integrity**: Read `02-bmad-state.md` and confirm `- Persona: BMad Master (Orchestrator)` is present. If corrupted, fix immediately.
2. **Verify artifact exists**: Check that the declared artifact file exists at the configured output path and is non-empty.
3. **Report results to user**: Confirm what was created and where, or report any verification failures.
```

**Why:** BMad Master already has delegation rules but no verification step. This adds a lightweight 3-step check that catches both state corruption (Bug 1) and missing artifacts (Bug 4) without restructuring the delegation flow. It acts as a safety net even if Fix A doesn't perfectly prevent corruption — BMad Master will catch and fix it.

---

## Testing Strategy

### Pre-Flight Verification

Before applying any changes, verify the exact line numbers in each file match this spec:

```bash
# Check that the bug patterns exist at expected locations
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/1-analysis/create-product-brief/steps/step-06-complete.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/2-plan-workflows/create-prd/steps-c/step-12-complete.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/3-solutioning/create-architecture/steps/step-08-complete.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/2-plan-workflows/create-ux-design/steps/step-14-complete.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/4-implementation/sprint-planning/checklist.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/4-implementation/dev-story/checklist.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/3-solutioning/create-epics-and-stories/steps/step-04-final-validation.md
grep -n 'cat >.*STATEEOF' skills/bmad-bmm/workflows/bmad-quick-flow/quick-spec/workflow.md
```

### Regression Tests (automated)

```bash
# 1. Regex patterns must still match patched state files
cd /a0/usr/projects/a0_bmad_method
python -m pytest tests/test_bmad_status_api.py tests/test_bmad_status_cli.py -v

# 2. All existing tests must pass
python -m pytest tests/ -v
```

### Manual Verification Checklist

After applying all changes, verify each fix:

#### Fix A Verification (8 files)
- [ ] **A1** step-06-complete.md: No `cat >` heredoc present; has `text_editor:patch` instructions; Phase=`2-planning`, Artifact=`product-brief.md`, Persona=`BMad Master (Orchestrator)`
- [ ] **A2** step-12-complete.md: No `cat >` heredoc present; has `text_editor:patch` instructions; Phase=`2-planning`, Artifact=`prd.md`, Persona=`BMad Master (Orchestrator)`
- [ ] **A3** step-08-complete.md: No `cat >` heredoc present; has `text_editor:patch` instructions; Phase=`3-solutioning`, Artifact=`architecture.md`, Persona=`BMad Master (Orchestrator)`
- [ ] **A4** step-14-complete.md: No `cat >` heredoc present; has `text_editor:patch` instructions; Phase=`3-solutioning`, Artifact=`ux-design-specification.md`, Persona=`BMad Master (Orchestrator)`
- [ ] **A5** sprint-planning/checklist.md: No `cat >` heredoc present; has `text_editor:patch` instructions; Phase=`4-implementation`, Artifact=`sprint-status.yaml`, Persona=`BMad Master (Orchestrator)`
- [ ] **A6** dev-story/checklist.md: No `cat >` heredoc present; has `text_editor:patch` instructions; Phase=`4-implementation`, Artifact=`story.md`, Persona=`BMad Master (Orchestrator)`
- [ ] **A7** step-04-final-validation.md: No `cat >` heredoc present; has `text_editor:patch` instructions; Phase=`4-implementation`, Artifact=`epics.md`, Persona=`BMad Master (Orchestrator)`
- [ ] **A8** quick-spec/workflow.md: No `cat >` heredoc present; has `text_editor:patch` instructions; Phase=`4-implementation`, Artifact=`quick-spec.md`, Persona=`BMad Master (Orchestrator)`

#### Fix B Verification (5 additions)
- [ ] **B1** bmad-agent-shared.md: New line `**Never write celebration/summary files**` present after line 187
- [ ] **B2** step-06-complete.md: Celebration text has `**Display to user (do NOT write to any file):**` prefix
- [ ] **B3** step-12-complete.md: Celebration text has `**Display to user (do NOT write to any file):**` prefix
- [ ] **B4** step-08-complete.md: Announcement text has `**Display to user (do NOT write to any file):**` prefix
- [ ] **B5** step-04-final-validation.md: Announcement text has `**Display to user (do NOT write to any file):**` prefix

#### Fix C Verification (1 addition)
- [ ] **C1** communication_additions.md: `## Post-Delegation Verification (MANDATORY)` section present after line 161 with all 3 verification steps

#### Regression Verification
- [ ] No `cat >` heredocs remain in any of the 8 completion step files
- [ ] No `$(date)` literal strings remain in any workflow file
- [ ] `bmad_status_core.py` regex `_PHASE_RE` matches `- Phase: 2-planning` format (unchanged)
- [ ] `bmad_status_core.py` regex `_ARTIFACT_RE` matches `- Active Artifact: product-brief.md` format (unchanged)
- [ ] All existing pytest tests pass

### End-to-End Workflow Test

After all changes applied and committed:

1. **Run Product Brief workflow** (CB) on a test project
   - Agent reads state file before patching
   - Agent applies `text_editor:patch` (not `cat >`)
   - State file preserves initiative context
   - Persona is `BMad Master (Orchestrator)` after completion
   - No stray files in project root
   - Artifact is at correct path and non-empty
   - BMad Master runs post-delegation verification

2. **Multi-workflow accumulation test**: Run Product Brief → PRD → Architecture
   - State accumulates correctly after each workflow
   - Initiative context survives all three workflows
   - No stray files after any workflow
   - BMad Master verification passes after each

3. **Status dashboard regression**: Run `bmad-status.py` after each workflow
   - Phase parsed correctly
   - Artifact parsed correctly
   - Dashboard renders without errors

---

## Boundaries

### Always
- Read each file before patching to verify line numbers match
- Preserve all content outside the changed sections
- Use exact text_editor:patch format shown in examples
- Reset Persona to `BMad Master (Orchestrator)` in every completion step
- Test that `bmad_status_core.py` regex patterns still match after changes
- Commit after each logical group of changes (Fix A, Fix B, Fix C)

### Ask First
- If line numbers don't match expected values (file may have been edited)
- If unexpected content found near the target sections
- If additional `cat >` heredoc patterns found outside the 8 listed files

### Never
- Never modify Python files (`bmad_status_core.py`, `_bmad_status.py`, etc.)
- Never modify `bmad-init.sh` or init scripts
- Never create new files — only modify existing ones
- Never delete files
- Never modify files in the upstream `BMAD-METHOD` repo (`.a0proj/upstream/`)
- Never change the state file schema or field names (would break regex patterns)
- Never remove the `Valid phase values` line from completion steps

---

## Not-Doing List

| Exclusion | Rationale |
|-----------|-----------|
| Python extension for automated verification | Prompt-based verification is simpler and aligns with Agent Zero philosophy. Can add later if needed. |
| `sed` approach (v1) | Not Agent Zero native. `text_editor:patch` has built-in freshness checks. |
| Restructuring completion step architecture | Too much change. Step files work; only the state write section needs fixing. |
| Adding config variable resolution checks | `bmad-agent-shared.md` already has resolution rules. Issue is agents not following them. |
| Modifying subordinate agent profiles | Bug is in workflow step instructions, not agent personas. |
| Changes to upstream BMAD-METHOD repo | We only modify our A0 adaptation layer. |
| Extension hook for automated verification (`process_chain_end`) | Too complex for this fix. Prompt-based approach first. |
| Context-adaptive discovery questions | Different issue (Mary's generic vision questions). Separate initiative. |
| Non-BMAD work tracking in state file | Schema change, separate initiative. |

---

## Success Criteria

### Per-Bug Acceptance Criteria

**Bug 1 — Persona State Corruption (Critical):**
- [ ] After any workflow completion, `02-bmad-state.md` contains `- Persona: BMad Master (Orchestrator)`
- [ ] No workflow completion step contains a `cat >` heredoc with a subordinate persona
- [ ] No workflow completion step references `code_execution_tool terminal` for state writes

**Bug 2 — Stray Summary Files (High):**
- [ ] `prompts/bmad-agent-shared.md` contains the `**Never write celebration/summary files**` rule
- [ ] All 4 completion steps with celebration/announcement text have `**Display to user (do NOT write to any file):**` prefix
- [ ] After running CB or CP workflow to completion, no unexpected files appear in project root

**Bug 3 — Full State File Overwrite (Critical):**
- [ ] After any workflow completion, initiative context in state file is preserved
- [ ] After any workflow completion, completed workflows list is preserved
- [ ] State file size grows (or stays similar) after completion — never shrinks to just 4 fields

**Bug 4 — No Post-Creation Verification (Medium):**
- [ ] `communication_additions.md` contains `## Post-Delegation Verification (MANDATORY)` section
- [ ] Verification section has all 3 steps: state integrity, artifact exists, report to user

**Bonus — `$(date)` Never Expands:**
- [ ] No `$(date` string literal exists in any workflow completion step
- [ ] State file `Last Updated` field contains an actual date (e.g., `2026-05-07`) after any workflow completion

### Regression Criteria
- [ ] All existing pytest tests pass without modification
- [ ] `bmad_status_core.py` `_PHASE_RE` regex matches patched state files
- [ ] `bmad_status_core.py` `_ARTIFACT_RE` regex matches patched state files
- [ ] Status dashboard renders correctly after state file patch

### Global Criteria
- [ ] 14 changes applied across 10 unique files
- [ ] 0 new files created
- [ ] 0 files deleted
- [ ] No Python files modified
- [ ] No upstream BMAD-METHOD files modified
- [ ] `git diff --stat` shows exactly 10 files changed

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Agent provides wrong current value in patch context | Low | Low | `text_editor:patch` freshness check rejects mismatched context; agent must re-read and retry |
| Agent ignores read-first instruction | Low | Medium | Step 1 is explicit "Read...to determine current field values"; example patch shows `<current value>` placeholders |
| Agent overwrites file instead of patching | Low | Critical | Instructions say "NEVER overwrite the entire file" in bold; example shows patch not full write; Fix C catches this |
| Multiple `- Phase:` lines in state file | Very Low | Low | `@@ - Phase:` anchor matches first occurrence; agent reads file first to verify structure |
| Agent ignores display-only instruction | Low | Low | Global rule in shared prompt + per-file directives = defense in depth |
| State file missing entirely | Very Low | Medium | Init must run first; `text_editor:patch` on missing file produces clear error |
| Race condition on shared state file | Very Low | High | Pre-existing condition; not introduced by this fix |
| Line numbers shifted since spec written | Medium | Medium | Pre-flight grep verification before applying patches |

---

## Open Questions — Resolved

All 5 open questions resolved via DeepWiki research against [BMAD-METHOD](https://github.com/bmad-code-org/BMAD-METHOD) upstream repo and local codebase verification:

1. **Anchor syntax: `@@ - Phase:` (field-level) ✅ Confirmed.** Upstream BMAD uses frontmatter (`stepsCompleted`, `inputDocuments`), not `@@` anchors. The `@@` pattern is our A0 adaptation for `text_editor:patch`. Field-level anchors are more precise — they target only lines needing update and won't break if other sections change.

2. **Persona valid values: No list needed ✅ Confirmed.** Upstream BMAD does NOT track persona in state file — persona is defined in agent `customize.toml` and adopted during activation. Our Persona field is entirely our A0 addition. Always using `BMad Master (Orchestrator)` is correct without a valid values list.

3. **Automation potential: 8 automated, 4 manual ✅ Confirmed.** 8 checks can be automated via grep/pytest (pre-flight line numbers, persona check, no `cat >` heredocs, no `$(date` literals, celebration guard exists, display-only prefixes, post-delegation section, regex regression). 4 require manual e2e verification (Product Brief workflow, multi-workflow accumulation, no stray files, BMad Master verification fires).

4. **Line number stability: Stable, pre-flight confirms ✅ Confirmed.** No target files edited since analysis. Implementation plan already includes pre-flight grep as step 1.

5. **Additional celebration/state-write patterns: None found ✅ Confirmed.** Grep'd all TEA, CIS, and BMB module directories — zero `cat >` heredoc patterns found. Upstream BMAD confirms celebration messages are "markdown response to the user" — never file writes. Only the 8 BMM files identified contain the bug pattern.

---

## Implementation Order

1. **Pre-flight:** Run grep verification to confirm line numbers (2 min)
2. **Fix A:** Apply all 8 completion step changes (mechanical, ~15 min)
3. **Fix B:** Apply global rule + 4 display-only wraps (~5 min)
4. **Fix C:** Apply BMad Master verification section (~2 min)
5. **Regression:** Run full test suite + grep verification (~5 min)
6. **Commit:** One commit per fix layer (A, B, C)
7. **E2E test:** Run Product Brief workflow on test project (manual)

---

## Supporting Documents

| Document | Path | Lines | Purpose |
|----------|------|-------|---------|
| Idea One-Pager | `.a0proj/ideas/bmad-state-fixes.md` | 78 | Problem statement, scope, exclusions |
| Fix Plan v2 | `/a0/usr/workdir/vps-analysis/bmad-fix-plan-v2.md` | 813 | Detailed before/after for all changes |
| Session Analysis | `/a0/usr/workdir/vps-analysis/bmad-consent-mode-analysis.md` | 415 | Real-world evidence of bugs |
| Conversation Backup | `/a0/usr/workdir/vps-analysis/consent-backup.txt` | 1418 | Original 198-turn session transcript |
