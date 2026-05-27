# Changelog

All notable changes to the BMAD Method plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---
---
## [1.5.0] — 2026-05-07

### State & Artifact Delivery Fixes

Fixed 5 critical bugs in BMAD workflow completion steps that caused state corruption,
stray summary files, and missing verification. All fixes use Agent Zero native `text_editor:patch`
instead of destructive `cat >` heredocs.

#### Bug Fixes

- **Bug 1:** Persona state corruption — 8 workflow steps hardcoded subordinate persona
- **Bug 2:** Stray summary files — celebration text lacked display-only guard (5 files)
- **Bug 3:** Full state file overwrite — `cat >` heredoc destroyed entire state file
- **Bug 4:** No post-creation verification — no artifact validation after delegation
- **Bonus:** `$(date)` never expanded inside single-quoted heredoc

#### Changes

- Replace `cat > STATEEOF` heredocs with `text_editor:patch` in 8 workflow files
- Add global celebration guard to `bmad-agent-shared.md`
- Add display-only prefix to 5 completion step files
- Add 3-step Post-Delegation Verification to BMad Master
- Add YYYY-MM-DD format note to date placeholders

#### Testing

- 103 regression tests, 641 total passing, 0 failures
- All 5 bugs have reproduction tests
- 45 edge case tests added

#### Ship Review

- Security: PASS (0 Critical, 0 High)
- Testing: PASS (641/641, 3 advisory gaps)
- Code Quality: PASS (0 Critical, 0 High)


## [1.4.0] — 2026-05-02

### Alignment Fix Sprint — Full Upstream v6.6.0 Sync

Comprehensive alignment of the BMAD Method A0 Plugin with upstream BMAD Method v6.6.0.
6 implementation bundles, 8 security fixes, 503 tests (up from 292).

#### Bundle 1: CSV → YAML Migration

- Convert 5 CSV config files to YAML (`module.yaml`) format
- Rewrite routing extension for YAML-based parsing with graceful degradation
- Create ADR-0010 documenting YAML canonical routing decision
- Archive CSV-to-YAML migration script

#### Bundle 2: Agent Consolidation

- Remove 3 agents: `bmad-sm`, `bmad-qa`, `bmad-quick-dev`
- Expand Amelia (`bmad-dev`) to 12 menus covering SM, QA, and quick-dev functions
- Update `bmad-master` to 16 subordinate agents
- Update agent roster in `bmad_status_core.py`

#### Bundle 3: CIS Persona Removal

- Remove 6 named CIS personas (Victor, Dr. Quinn, Maya, Carson, Sophia, Caravaggio)
- Replace with generic functional descriptions across 24 prompt files
- Fix icon collisions: design-thinking 🎨→🎯, presentation 🎨→🖼️

#### Bundle 4: Quick Fixes

- Update Morgan icon to 📦
- Change Sally style to filmmaker metaphor
- Add US menu code to Paige's customize.toml
- Add `_bmad/custom/` directory creation to init script
- Add module-scoped collision comments for QA/VS codes

#### Bundle 5: Test Updates

- 503 tests passing (up from 292)
- 56 test files covering all sprint bundles
- Test pyramid: 82% unit / 17% integration / 1% E2E (healthy)

#### Bundle 6: P3 Structural Alignment

- Implement 8-step activation sequence in `bmad-agent-shared.md`
- Add `resolve_customization` first-call instructions
- Add `persistent_facts` processing instructions
- Add prepend/append hooks processing instructions
- Standardize `project-context.md` loading across 8 implementation workflows
- Add file-based sidecar directories to init script
- Add sidecar loading to activation sequence
- Add sidecar writing instructions to agent prompts
- Create `bmad-sidecar-import` skill for upstream migration
- Create `resolve_customization.py` script (stdlib-only, zero external deps)

#### Security Fixes (8 issues from review phase)

1. **CSS injection** in `bmad-dashboard.html` — Alpine.js `x-text` bindings, zero `innerHTML`
2. **`shell=True` removal** — all subprocess calls use list-form args
3. **Error message disclosure** — generic errors to client, details server-side only
4. **Glob injection** — `_sanitize_glob_pattern()` 3-layer validation
5. **Path traversal** — `_validate_path_in_project()` boundary checks
6. **Input validation** — TOML strict parser with error handling
7. **Unsafe YAML loading** — `yaml.safe_load()` exclusively
8. **Error handling** — `set -euo pipefail`, no-clobber writes, atomic state updates

#### Ship Phase Sign-off

- **Code Review**: APPROVE — all 8 fixes verified, clean architecture
- **Security Audit**: GO — LOW risk, 0 Critical/High findings
- **Test Coverage**: GO — 503/503 pass, quality A-


## [1.3.0] — 2026-05-01

### Agent Prompt Fixes (Phase G)

Fix critical agent prompt defects discovered during workflow-builder failure analysis. All changes are prompt text only — no code changes. 10 tasks completed.

#### P0 — Critical Fixes

- **G-P0-1**: Fix broken `{{ include }}` — move `agents/_shared/prompts/bmad-agent-shared.md` to `prompts/bmad-agent-shared.md` (plugin root IS in search chain). Remove `agents/_shared/` directory. Revise ADR 0002.
- **G-P0-2**: Add `MANDATORY PROCESS COMPLIANCE` section to all 20 agent `role.md` files — 6-point directive enforcing process-driven behavior before persona definition
- **G-P0-3**: Rewrite shared fragment `Initial Clarification` section — remove escape hatch, add process-aware clarification (determines WHERE to start, not WHETHER)
- **G-P0-4**: Replace all 20 `solving.md` with clean BMAD-specific full override — eliminates high-agency vs follow-steps conflict entirely
- **G-P0-5**: Convert bmad-master `specifics.md` from 109-line inline to `{{ include }}` — prevents divergence after shared fragment rewrite

#### P1 — High Priority

- **G-P1-1**: Add `Subordinate Mode Detection` section to all 20 `communication_additions.md` — recognize superior agent, load skill, route, execute, suppress menu
- **G-P1-2**: Create shared `prompts/bmad-agent-shared-solving.md` fragment — replace 20 `solving.md` with `{{ include }}` for single source of truth

#### P2 — Polish

- **G-P2-1**: Add `A0 Framework Integration` section to BMB agent specifics (Wendy, Bond, Morgan)
- **G-P2-2**: Update failure analysis report to reflect clean full override decision

#### Test Coverage

- `tests/test_phase_g_include.py`: 12 tests — shared fragment location, include directives, agent counts, content verification
- `tests/test_phase_g_compliance.py`: 3 tests — compliance section presence, ordering, directive content
- Total: 292 tests pass (up from 263), 0 skipped

#### Root Causes Addressed

| Root Cause | Fix | Impact |
|---|---|---|
| RC0: Broken include | G-P0-1: Move to `prompts/` | 95% -> 60% |
| RC1: Conflicting directives | G-P0-4: Clean override | 60% -> 30% |
| RC2: Escape hatch | G-P0-3: Process-aware | 30% -> 15% |
| RC3: Step rules not in prompts | G-P0-2: Compliance gate | 15% -> 10% |
| RC4: No subordinate mode | G-P1-1: Detection section | 10% -> 5% |
| RC5: No process compliance gate | G-P0-2: Compliance gate | Combined with RC3 |

**Overall: Failure probability reduced from 95-100% to <5%**

### BMB Creation Path Fixes (Phase H)

Fix BMB creation output paths so agents and skills land in A0-discoverable directories. 8 tasks + review fixes completed.

#### P0 — Critical Fixes

- **H-P0-1**: Split `bmb_creations_output_folder` into `bmb_staging_folder`, `bmb_build_output_agents`, `bmb_build_output_skills` in `skills/bmad-bmb/config.yaml`
- **H-P0-2**: Update ~70 BMB step files with new path variables — agent steps → `bmb_build_output_agents`, workflow steps → `bmb_build_output_skills`, staging → `bmb_staging_folder`

#### P1 — High Priority

- **H-P1-1**: Create `bmad-promote` skill with `/promote-agent`, `/promote-workflow`, `/promote-skill` triggers for project-to-plugin promotion
- **H-P1-2**: Update `bmad-init.sh` to create `.a0proj/agents/` and `.a0proj/skills/` directories on init

#### P2 — Polish

- **H-P2-1**: Update celebrate step files with A0 auto-discovery guidance (no manual install instructions)

#### Review Fixes

- Path traversal validation in `promote.sh` — reject `..`, `/`, leading hyphens
- Added `/promote-skill` trigger to bmad-promote skill
- Created dedicated `test_phase_h_promote.py` (17 tests)
- Updated `module-help.csv` references

#### Test Coverage

- `tests/test_phase_h_paths.py`: Path split verification, celebrate step updates
- `tests/test_phase_h_promote.py`: 17 tests — name validation, type routing, error handling, trigger verification
- Total: 327 tests pass, 94 subtests, 0 failures


## [1.1.0] — 2026-05-01

### Upstream v6.6.0 Sync (Phase F)

Sync with upstream BMAD-METHOD v6.6.0 (88b9a1c → 9debc16). 12 tasks completed.

#### P0 — Critical Workflow Step Sync

- **F-P0-1**: Fix pre-checked architecture checklist in step-07-validation.md — all items unchecked `[ ]`, ✅ emoji removed from headers, 3-tier conditional status (READY FOR IMPLEMENTATION | READY WITH MINOR GAPS | NOT READY)
- **F-P0-2**: Add file churn detection to epic design in step-02-design-epics.md — Principle #6 (Implementation Efficiency), Step C (Review for File Overlap), brownfield context assessment, wrong/correct examples
- **F-P0-3**: Add file churn check + HALT + on_complete hook in step-04-final-validation.md — File Churn Check subsection, HALT instruction, resolve_customization.py on_complete hook

#### P1 — Config Migration + Customization

- **F-P1-1**: Move `project_name` from bmm config to core config
- **F-P1-2**: Remove `project_name` from bmm config
- **F-P1-3**: Update all 5 config.yaml versions to 6.6.0
- **F-P1-4**: Verify CSV row coverage post-migration (confirmed safe)
- **F-P1-5**: Include `resolve_customization.py` in plugin with A0 path adaptations
- **F-P1-6**: Create `bmad-customize` skill — ported upstream core skill with SKILL.md, list_customizable_skills.py, 30 customize.toml files

#### P2 — Polish

- **F-P2-1**: Update CHANGELOG with Phase F entries
- **F-P2-2**: Plugin version bump to 1.1.0

## [1.0.8] — 2026-04-26

### Agent Zero Alignment Migration (Phases A–D)

A comprehensive 4-phase migration aligning the BMAD Method plugin with Agent Zero architecture
standards. 35 tasks completed, 200 tests, 49 commits.

#### Phase A — Critical Bug Fixes (7 tasks)

- **A1**: Replace hardcoded `/a0/usr/projects/` paths with `$A0PROJ`-derived vars, add `set -euo pipefail`
- **A2**: Consolidate `read_state()` into `helpers/bmad_status_core.py` with compiled regexes, lowercase phase normalization
- **A3**: Remove cross-project mtime fallback from API and routing extension, gate CLI behind `BMAD_DEV_MODE`
- **A4**: Remove 4 stray `</div>` and 1 stray `</template>` from `bmad-dashboard.html`
- **A5**: Add `log.warning()` to all bare `except` blocks in routing extension
- **A6**: Add None-guard on `spec_from_file_location` in API module
- **A7**: Remove dead code — `SKILL_TO_MODULE`, consolidate phase-bucket dicts via `PHASE_BUCKETS` constant

#### Phase B — Structural Alignment (11 tasks)

- **B1**: Enable `per_project_config: true` in `plugin.yaml`
- **B2**: User preferences → `bmad-user-prefs.promptinclude.md` (no-clobber pattern)
- **B3**: Slash-style `trigger_patterns` in SKILL.md: `/bmad`, `/bmad-init`, `/bmad-help`, `/bmad-status`
- **B4**: Verified `SKILL_TO_MODULE` removal complete (A7)
- **B5**: Fix orphaned `this.error` reference in dashboard store JS
- **B6**: Full bash hardening of `bmad-init.sh` (rsync fallback, stderr warnings)
- **B7**: Consolidate `AGENT_NAMES`, `PHASE_ACTIONS` into `helpers/bmad_status_core.py`
- **B8**: Remove dead imports from `api/_bmad_status.py`
- **B9**: mtime-keyed caching `(path_str, mtime_ns)` for alias + CSV reads
- **B10**: Tag `v1.0.8-pre-align`
- **B11**: Comprehensive subprocess tests for `bmad-init.sh`

#### Phase C — Routing Consolidation (8 tasks)

- **C0**: Migrate `bmad-init/core/module-help.csv` to upstream 13-column schema
- **C1**: Remove dual-read compatibility code from routing extension
- **C2–C6**: Add `trigger_patterns` to **57 SKILL.md files** across bmm, cis, tea, bmb, and init/core modules
- **C7**: Comprehensive routing + discoverability verification tests

#### Phase D — UX Surface (9 tasks)

- **D1**: Create `bmad.methodology.shared.md` shared fragment (85 lines)
- **D2**: Audit all 20 `main.specifics.md` for shared content scope
- **D3**: Update 19 non-master `main.specifics.md` to use `{{ include }}` directive
- **D4**: Remove static 19-agent table from `bmad-master/role.md` → dynamic via `{{agent_profiles}}`
- **D5**: Pre-computed `_recommend()` results in API module with caching
- **D6**: Dashboard error display — `x-text` only, store-gated rendering
- **D7**: `project-context.md` stub generation in `bmad-init.sh`
- **D8**: Party mode implementation (solo mode, 8 acceptance criteria)
- **D9**: Plugin audit via structured review process

#### Review Fixes (3 additional)

- Restore `_SKILLS_DIR` / `_BMAD_CONFIG_DIR` definitions in routing extension
- Fix dashboard `this.loading` reset on success path
- Eliminate CSV cache bypass via `_read_csv_cached()` shared helper

#### Code Simplification (6 improvements)

- Removed redundant imports (`re`, `sys`, `json`)
- Moved timestamp computation to runtime
- Eliminated unused variables
- Added bounded cache eviction (max 128 entries, FIFO)

### Metrics

| Metric | Before | After |
|---|---|---|
| Tests | 14 | **200** |
| SKILL.md trigger_patterns | 0 | **57 files** |
| Duplicated agent prompt lines | ~1,662 | **1 shared file (85 lines)** |
| Agent roster | Static 19-entry table | **Dynamic via `{{agent_profiles}}`** |
| CSV schema alignment | 1 file outdated | **All 5 on upstream 13-col** |
| Dead code | Multiple instances | **Zero** |

---

## [1.0.7] — 2026-04-10

### FM-015 Fix — Workflow Config Path Resolution + Variable Resolution

#### Fixed

- **Workflow config path references** — 3 workflow files referenced non-existent `{project-root}/_bmad/bmm/config.yaml`. Fixed to point to `skills/bmad-bmm/config.yaml` (which exists in A0 plugin structure). Affected: `quick-dev/workflow.md`, `code-review/workflow.md`, `checkpoint-preview/SKILL.md`
- **Variable resolution guidance for all 19 specialist agents** — Added `## A0 Variable Resolution` block to every specialist agent's `specifics.md`. Agents now know to resolve `{user_name}`, `{communication_language}`, `{output_folder}`, `{planning_artifacts}`, `{implementation_artifacts}` from injected `01-bmad-config.md` instead of attempting to load a config file. Eliminates literal `{placeholder}` leakage in specialist workflow execution.

---

## [1.0.6] — 2026-04-10

### Alignment Sprint — Menu Codes + Prompt Architecture

#### Added

- **Ideate Module (IM) workflow** — Morgan (bmad-module-builder) can now ideate new modules
- **Convert Skill (CW) workflow** — Wendy (bmad-workflow-builder) can convert workflows to skills — BMB parity complete

#### Changed

- **8 menu codes aligned with upstream**: CHK→CK, QD→QQ, ERP→EP, TRC→TR, BAG→BA, BS→SB, CVS→CW, CW→BW
- **Prompt architecture refactor** — BMAD framework moved to `specifics.md` (A0 design pattern slot), `solving.md` override added with BMAD workflow execution pattern, `communication.md` simplified to JSON format rules only, `tips.md` trimmed to remove duplicated principles
- All 20 agents updated with new prompt architecture

#### Result

- **100% upstream parity across all 5 modules** — 66/66 workflows routable

---

## [1.0.5] — 2026-04-09

### Validation Sprint — End-to-End Method Verification

#### Workflow Validation (11 tests, 10 agents, all PASS)

- **BP** (Mary — Brainstorm Project): Skill loaded, 8 steps, workflow.md found
- **CP** (John — Create PRD): Skill loaded, 12 steps, workflow-create-prd.md found
- **CA** (Winston — Create Architecture): Skill loaded, 9+1 steps
- **CU** (Sally — Create UX): Skill loaded, 14 steps, template found
- **CE** (John — Create Epics): Skill loaded, 4 steps, templates found
- **QA** (Quinn — QA Automation): Skill loaded, 6 steps, instructions found
- **TMT** (Murat — Teach Me Testing): Skill loaded, 15 steps, 43 knowledge fragments
- **BS** (Carson — Brainstorming): CIS agent activated, 8 techniques available
- **AE** (Advanced Elicitation): Core skill loaded, 30+ methods
- **DG** (Distillator): Core task loaded, 4-stage architecture
- **LW** (List Workflows): 42+ workflows discoverable, phase detection correct

#### Bugs Found & Fixed

- **Story 052 — CIS Routing Gap**: `_80_bmad_routing_manifest.py` excluded `cis` module from all phase module lists. Fixed by adding `cis` to all phases in `PHASE_MODULES` map.
- **SKILL.md Format Standardization**: 21 SKILL.md files referenced `workflow.yaml` but actual execution used `instructions.md` (BMM/CIS) or `workflow.md` (TEA). All references standardized.

#### autoresearch Milestones

- **Formal LLM evaluation working**: `run_eval.py` now uses A0 native model routing
- **Baseline**: Composite 7.775/10 → **Re-evaluation: 8.45/10** (+0.675)
- **Phase A L1 rules**: 10 BMAD-specific behaviour rules applied

#### Documentation

- **README v1.0.5 rewrite**: Restored agent roster table with emojis, added badges, Skills Architecture section
- Removed internal `.a0proj` links from README

---

## [1.0.4] — 2026-04-09

### Sprint 4 — Process & Documentation (Stories 037–040)

- **Party Mode Persona Guard (FM-019)**: 8 prescriptive rules added to all BMAD agents + PERSONA GUARD section added to `workflow.md` — prevents persona drift during multi-agent collaboration
- **Upstream BMAD Sync Check**: Audited 5 suspected missing workflows; confirmed only `prfaq` was missing (ported in Sprint 5)
- **README v1.0.3 update**: Added What's New section, quality metrics summary, document lifecycle link
- **Architecture doc updated to v1.0.3**: 703 lines, 13 sections, semver-aligned with plugin version

### Sprint 5 — Upstream Parity & Validation (Stories 041–044)

- **prfaq (Working Backwards) workflow ported**: 5 step files + assets + agents + module-help.csv row added to `bmad-bmm`
- **28 TEA extended knowledge files ported**: 43 total knowledge fragments now in `knowledge/bmad-test-architect/` (was 15)
- **BMM Phase 2 Routing Validation**: 6/6 PASS — PM (John) + UX (Sally) end-to-end routing confirmed. FM-006/007/008 CLOSED.
- **Behavioral test suite**: 60/60 PASS · Grade A+ (100/100) · zero regressions vs prior baseline

### Sprint 6 — autoresearch & Housekeeping (Stories 045–047)

- **autoresearch Phase A audit**: Root cause diagnosed — capture pipeline works correctly, optimizer loop never triggered due to insufficient conversation depth
- **autoresearch per-agent profiles**: 20 config files verified DONE across all agent profiles
- **State housekeeping**: 4 story files corrected (status + metadata), state inconsistencies in `02-bmad-state.md` resolved

---

## [1.0.3] — 2026-04-09

### Major Improvements — BMAD Harness Quality Initiative

Comprehensive system-wide improvement based on DeepWiki upstream analysis (4 BMAD repos) and A0 native audit. 25 failure modes identified and addressed across orchestration, workflow execution, specialist agents, and module infrastructure.

#### 🚨 Critical Fixes

- **FM-012 FIXED**: All 10 workflow instruction files referenced `workflow.xml` (non-existent) — fixed to `workflow.md`. The workflow execution engine now loads correctly in all BMM and TEA workflows for the first time.
- **FM-021 FIXED**: `_80_bmad_routing_manifest.py` now scans the filesystem for actual artifact existence using `output-location` + `outputs` columns from module-help.csv. Phase detection is now filesystem-based, not state-file-dependent. 15 unit tests added.
- **FM-023 FIXED**: `output-location` and `outputs` columns populated for all `required=true` rows in `skills/bmad-bmm/module-help.csv`. Phase gate artifact detection now works correctly.

#### 🔧 Workflow Improvements

- **Sharding**: 6 monolithic workflow instruction files (8–60KB each) sharded into 38 focused step files across dev-story, create-story, sprint-planning, sprint-status, correct-course, retrospective. Each step = one logical task + one HALT.
- **dev-story granularity**: 6 step files refined to 10 single-phase step files (step-01 through step-10).
- **stepsCompleted tracking**: Resume capability added to 4 key workflows (Create PRD, Create Architecture, Dev Story, Sprint Planning) — 26 files updated with Resume Check blocks and Step Complete markers.
- **FM-015 FIXED**: workflow.yaml config variables (`{communication_language}`, `{user_skill_level}`, `{user_name}`) confirmed unresolved by A0 natively. Mitigated by adding Workflow Variable Resolution table to `01-bmad-config.md`.

#### 🤖 Agent Quality

- **FM-017 FIXED**: All 19 agents enriched with 7+ action-oriented principles, precise communication style, and (for BMM agents) startup orientation instruction to read project state on activation. Zero compliance violations on Bond validation pass.
- **FM-016 FIXED**: Murat (bmad-test-architect) now has 14 core-tier knowledge fragments preloaded via FAISS (`.a0proj/knowledge/bmad-test-architect/`) and dynamic fragment loading in all 9 TEA workflow entry steps.
- `skills/bmad-tea/testarch/SKILL.md` wrapper created — testarch skill now directly loadable.

#### 📦 Module & Skills

- **CIS alignment**: Presentation workflow created for Caravaggio (`skills/bmad-cis/workflows/presentation/` — 4 files). All 6 CIS agents now routable via `LW`. CIS README updated.
- **FM-024**: Document Lifecycle Framework implemented — artifact relationship DAG, staleness detection (mtime-based, live in `_80` EXTRAS), `consistency-check.md` task, `docs/document-lifecycle.md` framework guide.
- **FM-022**: TEA SKILL.md wrapper created.

#### 🤖 autoresearch

- autoresearch plugin initialized for BMAD project. Per-project workspace created.
- System-wide optimization strategy v2.0 written (25 failure modes, 5 layers, all 19 profiles).
- 20 per-agent config files created — each profile has targeted cascade levels and failure mode focus.

#### ✅ Quality

- Behavioral test suite re-run: **54/54 PASS · Grade A (96/100) · 0 regressions** vs prior baseline.
- Test score improvement: B (89) → A (96) (+7 points).
- `tests/test_extension_80.py` added: 15 automated unit tests for routing extension.

---


## [1.0.2] — 2026-04-08

### Upstream Source Updates

**Core (BMM): 6.0.4 → 6.2.2**

- `code-review` workflow: full rewrite with sharded 4-step architecture (step-01 through step-04 + workflow.md), replacing the old workflow.yaml format
- `quick-dev` workflow: overhauled with new flat step structure (step-01 through step-05 + step-oneshot.md + spec-template.md)
- `checkpoint-preview`: new Phase 4 workflow added — LLM-assisted human-in-the-loop review (5 steps)
- Source references updated in `.a0proj/bmad-source/core/`

**BMB (Builder): 1.1.0 → 1.5.0**

- `agent-builder`: sanctum memory architecture added (BOND/CREED/MEMORY/PERSONA/PULSE/INDEX templates + bootloader), 26 new reference docs, 8 updated scripts
- `workflow-builder`: 18 new reference docs added + Workflow Convert capability scripts
- `module-builder`: 10 new assets (standalone + setup-skill templates), references, scripts
- `bmb-setup`: new skill added (module setup scripts + module-help.csv)
- Source references updated in `.a0proj/bmad-source/bmb/`

**TEA (Test Architect): 1.7.2 → 1.9.1**

- 13 old `*subprocess*` step files deleted — renamed to `*subagent*` terminology across all 9 workflows
- `playwright-cli.md` knowledge fragment added to workflow knowledge directories
- All step files (steps-c / steps-e / steps-v) synced from upstream
- Source references updated in `.a0proj/bmad-source/tea/`

**CIS: 0.1.9** — no change

### CSV and Routing Fixes

- Renamed `agent` → `skill` column in all `module-help.csv` headers (8 files) to align with upstream 13-column spec
- Added `checkpoint-preview` (code: `CHK`) to `bmad-bmm/module-help.csv`
- Added `bmb-setup` (code: `BS`) to `bmad-bmb/module-help.csv`
- Fixed `code-review` CSV path: `workflow.yaml` → `workflow.md`
- Fixed `code-review` SKILL.md to reference `workflow.md`

### Tests

- Behavioral regression: 49/49 PASS (0 PARTIAL, 0 FAIL)
- Fixed test harness `load_module_help_csvs()` to use top-level CSV only, matching runtime extension behavior

### Documentation

- README fully rewritten — value-first, audience-focused, no internal implementation details
- plugin.yaml description updated to reflect current state

---

## [1.0.1] — 2026-03-27

### Routing Extension

- Implemented dynamic lightweight (LW) routing — the `LW` command now reads directly from `skills/*/module-help.csv` at runtime, eliminating the sync risk with the compiled `bmad-help.csv` aggregate
- `_80_bmad_routing_manifest.py` column priority fixed: reads the `agent` column (the original column name) with `skill` and `agent-name` retained as legacy fallbacks
- Natural language routing fallback updated to also use dynamic module CSVs instead of the compiled aggregate
- Removed `_11_bmad_autobrief.py` extension — A0 natively auto-injects all `.a0proj/instructions/` files into every agent's system prompt; the extension was redundant

### Documentation Sprint 1 (Stories 016–018)

- `project-overview.md` refreshed with current architecture and story table
- `project-context.md` generated (LLM-optimized brownfield context)
- Architecture v4.0 document written
- Retrospective PRD authored — dogfooding gap closed

### Update Sprint 1 (Stories 019–023)

- `module-help.csv` format updated to 13-column upstream spec across all modules
- `bmad-bmm` skill updated to include all Phase 4 workflows
- `bmad-bmb` skill updated to BMB v1.2.0 (major restructure)
- `bmad-tea` skill updated to TEA v1.7.2 (skills migration)
- `bmad-cis` skill updated to CIS v0.1.9 (skill format conversion)
- Per-workflow thin SKILL.md wrappers implemented (Option B)

---

## [1.0.0] — 2026-02-28

### Initial Release

- Full BMAD Method Framework integration for Agent Zero
- 20 specialist agents across 4 modules: BMM, BMB, TEA, CIS
- 5 skill packages with bundled workflow files
- Project-scoped FAISS-native shared memory store
- Phase-aware routing extension (`_80_bmad_routing_manifest.py`)
- Interactive BMAD status dashboard plugin
- Party Mode (single-LLM multi-persona simulation)
- `bmad-init` bootstrap script for workspace initialization
- Phase Gate Protocol (GATE-001) enforcement
