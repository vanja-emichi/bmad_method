# Sprint Planning Validation Checklist

## Core Validation

### Complete Coverage Check

- [ ] Every epic found in epic\*.md files appears in sprint-status.yaml
- [ ] Every story found in epic\*.md files appears in sprint-status.yaml
- [ ] Every epic has a corresponding retrospective entry
- [ ] No items in sprint-status.yaml that don't exist in epic files

### Parsing Verification

Compare epic files against generated sprint-status.yaml:

```
Epic Files Contains:                Sprint Status Contains:
✓ Epic 1                            ✓ epic-1: [status]
  ✓ Story 1.1: User Auth              ✓ 1-1-user-auth: [status]
  ✓ Story 1.2: Account Mgmt           ✓ 1-2-account-mgmt: [status]
  ✓ Story 1.3: Plant Naming           ✓ 1-3-plant-naming: [status]
                                      ✓ epic-1-retrospective: [status]
✓ Epic 2                            ✓ epic-2: [status]
  ✓ Story 2.1: Personality Model      ✓ 2-1-personality-model: [status]
  ✓ Story 2.2: Chat Interface         ✓ 2-2-chat-interface: [status]
                                      ✓ epic-2-retrospective: [status]
```

### Final Check

- [ ] Total count of epics matches
- [ ] Total count of stories matches

## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `4-implementation`
   - `Active Artifact` → `sprint-status.yaml`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date (YYYY-MM-DD format)
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

Valid phase values: `ready` | `1-analysis` | `2-planning` | `3-solutioning` | `4-implementation` | `bmb` | `cis`
- [ ] All items are in the expected order (epic, stories, retrospective)
