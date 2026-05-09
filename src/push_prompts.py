"""
Script to push optimized prompts to the LangSmith Prompt Hub.

This script:
1. Reads the optimized prompt from prompts/bug_to_user_story_v2.yml
2. Validates the prompt structure
3. Builds a ChatPromptTemplate (system + human messages)
4. Pushes it publicly to LangSmith Hub as {username}/bug_to_user_story_v2
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure
from pathlib import Path

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"
V2_FILE = PROMPTS_DIR / "bug_to_user_story_v2.yml"


def validate_prompt(prompt_data: dict) -> tuple:
    """
    Validates the prompt structure before pushing to LangSmith Hub.

    Args:
        prompt_data: Dict loaded from the YAML file

    Returns:
        (is_valid, errors) tuple
    """
    return validate_prompt_structure(prompt_data)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Pushes an optimized prompt to LangSmith Hub as a public repo.

    Args:
        prompt_name: Full hub name, e.g. "username/bug_to_user_story_v2"
        prompt_data: Dict with system_prompt, user_prompt and metadata

    Returns:
        True on success, False on failure
    """
    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "")

    if not system_prompt or not user_prompt:
        print("system_prompt or user_prompt is empty — aborting push")
        return False

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", user_prompt),
    ])

    try:
        print(f"Pushing to hub: {prompt_name}")
        hub.push(prompt_name, prompt_template, new_repo_is_public=False)
        print(f"Push successful — prompt available at:")
        print(f"  https://smith.langchain.com/prompts/{prompt_name}")
        return True

    except Exception as e:
        # "Nothing to commit" means prompt is already up-to-date — treat as success
        if "Nothing to commit" in str(e):
            print("Prompt already up-to-date on hub (no changes detected)")
            print(f"  https://smith.langchain.com/prompts/{prompt_name}")
            return True
        print(f"Error pushing prompt: {e}")
        return False


def main():
    """Main entry point."""
    print_section_header("PUSHING OPTIMIZED PROMPTS TO LANGSMITH HUB")

    required = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required):
        return 1

    username = os.getenv("USERNAME_LANGSMITH_HUB")

    # Load v2 YAML
    print(f"Loading: {V2_FILE}")
    data = load_yaml(str(V2_FILE))
    if not data:
        print(f"Failed to load {V2_FILE}")
        return 1

    prompt_key = "bug_to_user_story_v2"
    if prompt_key not in data:
        print(f"Key '{prompt_key}' not found in YAML")
        return 1

    prompt_data = data[prompt_key]

    # Validate before pushing
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("Validation passed\n")

    # Push using just the prompt name (no owner prefix).
    # When USERNAME_LANGSMITH_HUB="-", evaluate.py pulls as "-/name",
    # which maps to the workspace's no-owner prompts in LangSmith.
    success = push_prompt_to_langsmith(prompt_key, prompt_data)

    if success:
        print("\nNext step: run evaluation")
        print("  python src/evaluate.py")
        return 0
    else:
        print("\nPush failed. Check your credentials and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
