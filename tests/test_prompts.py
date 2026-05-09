"""
Automated tests for validating the optimized prompt (v2).
"""
import pytest
import yaml
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str) -> dict:
    """Load prompts from a YAML file."""
    with open(file_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestPrompts:
    def setup_method(self):
        data = load_prompts(PROMPT_FILE)
        self.prompt = data["bug_to_user_story_v2"]
        self.system_prompt = self.prompt.get("system_prompt", "")
        self.user_prompt = self.prompt.get("user_prompt", "")
        self.full_text = self.system_prompt + self.user_prompt

    def test_prompt_has_system_prompt(self):
        """Verify that 'system_prompt' field exists and is not empty."""
        assert "system_prompt" in self.prompt, "Field 'system_prompt' is missing"
        assert self.system_prompt.strip(), "system_prompt must not be empty"

    def test_prompt_has_role_definition(self):
        """Verify that the prompt defines a persona (e.g., 'Product Manager')."""
        role_keywords = [
            "Product Manager",
            "Você é um",
            "You are a",
            "Sênior",
            "especialista",
            "expert",
        ]
        found = any(kw in self.system_prompt for kw in role_keywords)
        assert found, (
            "system_prompt must define a role/persona "
            f"(none of {role_keywords} found)"
        )

    def test_prompt_mentions_format(self):
        """Verify that the prompt requires Markdown or standard User Story format."""
        format_keywords = [
            "Como um",
            "eu quero",
            "para que",
            "Critérios de Aceitação",
            "User Story",
            "Dado que",
            "Markdown",
        ]
        found = any(kw in self.system_prompt for kw in format_keywords)
        assert found, (
            "system_prompt must specify an output format "
            f"(none of {format_keywords} found)"
        )

    def test_prompt_has_few_shot_examples(self):
        """Verify that the prompt contains input/output examples (Few-shot technique)."""
        example_keywords = [
            "Exemplo",
            "exemplo",
            "Example",
            "Bug Report:",
            "User Story:",
        ]
        found = any(kw in self.system_prompt for kw in example_keywords)
        assert found, (
            "system_prompt must contain few-shot examples "
            f"(none of {example_keywords} found)"
        )

    def test_prompt_no_todos(self):
        """Ensure no [TODO] placeholders remain in the prompt text."""
        assert "[TODO]" not in self.full_text, (
            "Prompt still contains '[TODO]' placeholders — remove them before submitting"
        )

    def test_minimum_techniques(self):
        """Verify (via YAML metadata) that at least 2 techniques are listed."""
        techniques = self.prompt.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Expected at least 2 techniques in 'techniques_applied', "
            f"found {len(techniques)}: {techniques}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
