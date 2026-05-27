# BMAD State & Artifact Delivery Fixes — Implementation Plan

**Source of truth:** `SPEC.md` (1,087 lines)
**Date:** 2026-05-07
**Branch:** `develop` → `main` on `/ship`
**Scope:** 14 changes across 10 unique files. 0 new files. 0 deletions.

---

## 1. Overview

Fix 4 critical bugs (+1 bonus) in the BMAD Method plugin's workflow completion steps that cause state corruption, stray files, and missing verification. All fixes are prompt/instruction-only — no Python code changes.

**3-Layer Fix:**
- **Fix A (8 files):** Replace destructive `cat >` heredocs with Agent Zero native `text_editor:patch` instructions → fixes Bug 1 (persona corruption), Bug 3 (full overwrite), Bonus (`$(date)` never expands)
- **Fix B (5 additions):** Add celebration message "display-only" guards → fixes Bug 2 (stray summary files)
- **Fix C (1 addition):** Add post-delegation verification to BMad Master → fixes Bug 4 (no post-creation verification)

---

## 2. Dependency Graph

```
Task 0: Pre-flight verification
    │
    ├──→ Task 1: A4 step-14-complete.md (A only) ──────────┐
    ├──→ Task 2: A5 sprint-planning/checklist.md (A only) ──┤
    ├──→ Task 3: A6 dev-story/checklist.md (A only) ────────┤
    ├──→ Task 4: A8 quick-spec/workflow.md (A only) ────────┤
    │                                                       │
    ├──→ Task 5: A1+B2 step-06-complete.md ────────────────┤
    ├──→ Task 6: A2+B3 step-12-complete.md ────────────────┤  Fix A
    ├──→ Task 7: A3+B4 step-08-complete.md ────────────────┤  complete
    ├──→ Task 8: A7+B5 step-04-final-validation.md ────────┤  (all 8)
    │                                                       │
    ├──→ Task 9: B1 bmad-agent-shared.md (B only) ─────────┤  (independent)
    │                                                       │
    │                          ┌────────────────────────────┘
    │                          │ depends on Fix A
    └──→ Task 10: C1 communication_additions.md (C only)
                │
                └──→ Task 11: Regression tests
                         │
                         └──→ Task 12: Git commits
```

**Parallelization:** Tasks 1–9 are all independent after Task 0. Task 10 depends on Fix A (Tasks 1–8) being complete.

---

## 3. Execution Strategy

### Phase 1: Pre-flight (Sequential)
Run grep verification to confirm all bug patterns exist at expected line numbers. Fail fast if any pattern is missing.

### Phase 2: Fix A + Fix B (Parallel)
Apply all 8 Fix A replacements and 5 Fix B additions. Tasks 1–9 can run in parallel since they touch different files. Four files get both Fix A and Fix B in the same task.

**Checkpoint A:** After all Fix A files patched — no `cat >` heredocs remain, no `$(date)` literals remain.

### Phase 3: Fix C (Sequential, after Fix A)
Add post-delegation verification to BMad Master. Depends on Fix A being applied (otherwise verification would always fail because state files are still being corrupted).

**Checkpoint B:** After Fix C — `## Post-Delegation Verification (MANDATORY)` section present.

### Phase 4: Regression + Commit (Sequential)
Run full test suite, grep verification, and commit per fix layer.

**Checkpoint C:** All tests pass, `git diff --stat` shows exactly 10 files.

---

## 4. Task Breakdown

### Task 0: Pre-flight Verification

| Field | Value |
|-------|-------|
| **Size** | XS |
| **Depends on** | None |
| **Files** | None (read-only grep checks) |

Verify all 8 bug patterns exist at expected locations using grep. Check line numbers for B1 insertion point and C1 insertion point.

---

### Tasks 1–4: Fix A — A-only Files (4 tasks)

Each task replaces the `## Workflow Completion — State Write (MANDATORY)` section with the `text_editor:patch` version. Phase, Artifact, and Persona values vary per file.

| Task | Change | File (short) | Phase | Artifact |
|------|--------|-------------|-------|----------|
| 1 | A4 | step-14-complete.md | 3-solutioning | ux-design-specification.md |
| 2 | A5 | sprint-planning/checklist.md | 4-implementation | sprint-status.yaml |
| 3 | A6 | dev-story/checklist.md | 4-implementation | story.md |
| 4 | A8 | quick-spec/workflow.md | 4-implementation | quick-spec.md |

---

### Tasks 5–8: Fix A+B — Dual-change Files (4 tasks)

Each task does two things to the same file:
1. Replace the `cat >` heredoc section with `text_editor:patch` instructions (Fix A)
2. Add `**Display to user (do NOT write to any file):**` prefix to celebration/announcement text (Fix B)

| Task | Changes | File (short) | Phase | Artifact | Celebration line |
|------|---------|-------------|-------|----------|-----------------|
| 5 | A1+B2 | step-06-complete.md | 2-planning | product-brief.md | "Congratulations on completing the Product Brief..." |
| 6 | A2+B3 | step-12-complete.md | 2-planning | prd.md | "Congratulations on completing the PRD..." |
| 7 | A3+B4 | step-08-complete.md | 3-solutioning | architecture.md | "The architecture will serve as..." |
| 8 | A7+B5 | step-04-final-validation.md | 4-implementation | epics.md | "Offer to answer any questions..." |

---

### Task 9: Fix B1 — Global Celebration Guard

| Field | Value |
|-------|-------|
| **Size** | XS |
| **Depends on** | Task 0 |
| **Files** | `prompts/bmad-agent-shared.md` |

Insert `**Never write celebration/summary files**` rule after line 187 in the "File and Artifact Handling" section.

---

### Task 10: Fix C1 — Post-Delegation Verification

| Field | Value |
|-------|-------|
| **Size** | XS |
| **Depends on** | Tasks 1–8 (Fix A must be complete) |
| **Files** | `agents/bmad-master/prompts/agent.system.main.communication_additions.md` |

Insert `## Post-Delegation Verification (MANDATORY)` section after line 161 with 3 verification steps.

---

### Task 11: Regression Tests

| Field | Value |
|-------|-------|
| **Size** | S |
| **Depends on** | Tasks 1–10 (all fixes applied) |
| **Files** | None (verification only) |

Run automated regression: pre-flight grep (inverse), pytest suite, manual verification checklist.

---

### Task 12: Git Commits

| Field | Value |
|-------|-------|
| **Size** | XS |
| **Depends on** | Task 11 (tests pass) |
| **Files** | None (git operations) |

Three commits: one per fix layer (A, B, C).

---

## 5. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Line numbers shifted since SPEC written | Med | Pre-flight grep verification (Task 0) catches before any changes |
| Agent provides wrong current value in patch context | Low | `text_editor:patch` freshness check rejects mismatched context |
| Agent overwrites file instead of patching | Critical | Instructions say "NEVER overwrite" in bold; Fix C catches this |
| Multiple `- Phase:` lines in state file | Low | `@@ - Phase:` anchor matches first occurrence |
| `bmad_status_core.py` regex breaks | High | Regression test catches; regex format unchanged by fix |

---

## 6. Open Questions

None — all 5 original questions resolved in SPEC.md §Open Questions — Resolved.
