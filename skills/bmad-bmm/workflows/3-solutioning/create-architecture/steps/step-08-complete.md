# Step 8: Architecture Completion & Handoff

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER generate content without user input

- 📖 CRITICAL: ALWAYS read the complete step file before taking any action - partial understanding leads to incomplete decisions
- ✅ ALWAYS treat this as collaborative completion between architectural peers
- 📋 YOU ARE A FACILITATOR, not a content generator
- 💬 FOCUS on successful workflow completion and implementation handoff
- 🎯 PROVIDE clear next steps for implementation phase
- ⚠️ ABSOLUTELY NO TIME ESTIMATES - AI development speed has fundamentally changed
- ✅ YOU MUST ALWAYS SPEAK OUTPUT In your Agent communication style with the config `{communication_language}`

## EXECUTION PROTOCOLS:

- 🎯 Show your analysis before taking any action
- 🎯 Present completion summary and implementation guidance
- 📖 Update frontmatter with final workflow state
- 🚫 THIS IS THE FINAL STEP IN THIS WORKFLOW

## YOUR TASK:

Complete the architecture workflow, provide a comprehensive completion summary, and guide the user to the next phase of their project development.

## COMPLETION SEQUENCE:

### 1. Congratulate the User on Completion

Both you and the User completed something amazing here - give a summary of what you achieved together and really congratulate the user on a job well done.

### 2. Update the created document's frontmatter

```yaml
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '{{current_date}}'
```

### 3. Next Steps Guidance

Architecture complete. Read fully and follow: `{project-root}/skills/bmad-init/core/tasks/help.md`

Upon Completion of task output: offer to answer any questions about the Architecture Document.


## SUCCESS METRICS:

✅ Complete architecture document delivered with all sections
✅ All architectural decisions documented and validated
✅ Implementation patterns and consistency rules finalized
✅ Project structure complete with all files and directories
✅ User provided with clear next steps and implementation guidance
✅ Workflow status properly updated
✅ User collaboration maintained throughout completion process

## FAILURE MODES:

❌ Not providing clear implementation guidance
❌ Missing final validation of document completeness
❌ Not updating workflow status appropriately
❌ Failing to celebrate the successful completion
❌ Not providing specific next steps for the user
❌ Rushing completion without proper summary

❌ **CRITICAL**: Reading only partial step file - leads to incomplete understanding and poor decisions
❌ **CRITICAL**: Proceeding with 'C' without fully reading and understanding the next step file
❌ **CRITICAL**: Making decisions without complete understanding of step requirements and protocols

## WORKFLOW COMPLETE:

This is the final step of the Architecture workflow. The user now has a complete, validated architecture document ready for AI agent implementation.

## Workflow Completion — State Update (MANDATORY)

Before returning control to the user, update the project state file using `text_editor:patch`:

1. Read `{project-root}/instructions/02-bmad-state.md` to determine current field values
2. Apply a `text_editor:patch` with `patch_text` that updates ONLY these fields:
   - `Phase` → `3-solutioning`
   - `Active Artifact` → `architecture.md`
   - `Persona` → `BMad Master (Orchestrator)` **(ALWAYS reset to this value — never your own persona)**
   - `Last Updated` → today's date (YYYY-MM-DD format)
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

Valid phase values: `ready` | `1-analysis` | `2-planning` | `3-solutioning` | `4-implementation` | `bmb` | `cis`

**Display to user (do NOT write to any file):** The architecture will serve as the single source of truth for all technical decisions, ensuring consistent implementation across the entire project development lifecycle.

---
## ✅ Step Complete

Append `step-08-complete` to the `stepsCompleted` array in this document's frontmatter.
Update `lastUpdatedAt` with current ISO timestamp.
Then HALT and await user instruction before proceeding to the next step.
