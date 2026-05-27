"""Phase F - P0 workflow step sync verification tests (F-P0-1/2/3)."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STEP_07 = ROOT / 'skills' / 'bmad-bmm' / 'workflows' / '3-solutioning' / 'create-architecture' / 'steps' / 'step-07-validation.md'
STEP_02 = ROOT / 'skills' / 'bmad-bmm' / 'workflows' / '3-solutioning' / 'create-epics-and-stories' / 'steps' / 'step-02-design-epics.md'
STEP_04 = ROOT / 'skills' / 'bmad-bmm' / 'workflows' / '3-solutioning' / 'create-epics-and-stories' / 'steps' / 'step-04-final-validation.md'


class TestStep07Validation(unittest.TestCase):
    """F-P0-1: step-07-validation.md - unchecked checklist, 3-tier status."""

    def setUp(self):
        self.text = STEP_07.read_text()

    def test_has_unchecked_checklist_items(self):
        """Checklist must contain unchecked [ ] items."""
        self.assertRegex(self.text, r'\[ \]',
                         'step-07 has no unchecked [ ] checklist items')

    def test_no_prechecked_checklist_items(self):
        """Checklist line items must NOT start as pre-checked [x].
        Note: [x] may appear in instruction text explaining how to mark."""
        lines = self.text.splitlines()
        checklist_lines = [l for l in lines if re.match(r'\s*- \[[ x]\]', l)]
        pre_checked = [l for l in checklist_lines if re.match(r'\s*- \[x\]', l)]
        self.assertEqual(len(pre_checked), 0,
                         f'Found pre-checked [x] lines: {pre_checked[:5]}')

    def test_has_3_tier_conditional_status(self):
        """Must have 3-tier status: READY FOR IMPLEMENTATION | READY WITH MINOR GAPS | NOT READY."""
        self.assertIn('READY FOR IMPLEMENTATION', self.text)
        self.assertIn('READY WITH MINOR GAPS', self.text)
        self.assertIn('NOT READY', self.text)

    def test_starts_with_heading(self):
        """step-07 uses # heading style - verify structure preserved."""
        self.assertTrue(self.text.startswith('# Step 7'),
                        'step-07 does not start with expected heading')

    def test_step_complete_section_exists(self):
        """Must have Step Complete section (A0-specific)."""
        self.assertIn('Step Complete', self.text,
                      'step-07 missing Step Complete section')


class TestStep02DesignEpics(unittest.TestCase):
    """F-P0-2: step-02-design-epics.md - Principle #6, Step C."""

    def setUp(self):
        self.text = STEP_02.read_text()

    def test_has_implementation_efficiency_principle(self):
        """Must contain Principle #6: Implementation Efficiency."""
        self.assertIn('Implementation Efficiency', self.text,
                      'step-02 missing Implementation Efficiency principle')

    def test_has_step_c_file_overlap_review(self):
        """Must contain Step C: Review for File Overlap."""
        self.assertIn('File Overlap', self.text,
                      'step-02 missing File Overlap Review step')

    def test_yaml_frontmatter_preserved(self):
        """Must start with YAML frontmatter (A0-specific)."""
        self.assertTrue(self.text.startswith('---'),
                        'step-02 does not start with YAML frontmatter')

    def test_frontmatter_has_name(self):
        """YAML frontmatter must have name field."""
        self.assertIn("name: 'step-02-design-epics'", self.text)

    def test_has_path_definitions(self):
        """Must contain A0 path definitions section."""
        self.assertIn('workflow_path', self.text,
                      'step-02 missing workflow_path definition')


class TestStep04FinalValidation(unittest.TestCase):
    """F-P0-3: step-04-final-validation.md - File Churn, HALT, on_complete."""

    def setUp(self):
        self.text = STEP_04.read_text()

    def test_has_file_churn_check(self):
        """Must contain File Churn Check."""
        self.assertIn('File Churn', self.text,
                      'step-04 missing File Churn Check')

    def test_has_halt_instruction(self):
        """Must contain HALT instruction."""
        self.assertIn('HALT', self.text,
                      'step-04 missing HALT instruction')

    def test_has_resolve_customization_reference(self):
        """Must reference resolve_customization.py in on_complete hook."""
        self.assertIn('resolve_customization.py', self.text,
                      'step-04 missing resolve_customization.py reference')

    def test_uses_a0_path_convention(self):
        """Must use $A0PROJ/_bmad/ not {project-root}/_bmad/."""
        self.assertIn('$A0PROJ/_bmad', self.text,
                      'step-04 does not use $A0PROJ path convention')

    def test_yaml_frontmatter_preserved(self):
        """Must start with YAML frontmatter (A0-specific)."""
        self.assertTrue(self.text.startswith('---'),
                        'step-04 does not start with YAML frontmatter')

    def test_frontmatter_has_name(self):
        """YAML frontmatter must have name field."""
        self.assertIn("name: 'step-04-final-validation'", self.text)

    def test_has_state_update_section(self):
        """Must have State Update section (A0-specific)."""
        self.assertIn('State Update', self.text,
                      'step-04 missing State Update section')
