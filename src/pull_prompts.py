"""
Script to pull prompts from the LangSmith Prompt Hub.

This script:
1. Connects to LangSmith using credentials from .env
2. Pulls the baseline prompt: leonanluppi/bug_to_user_story_v1
3. Saves it locally as prompts/bug_to_user_story_v1.yml
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

SOURCE_PROMPT = "leonanluppi/bug_to_user_story_v1"
LOCAL_FILE = PROMPTS_DIR / "bug_to_user_story_v1.yml"


def extract_prompt_data(prompt_template) -> dict:
    """
    Extracts message content from a ChatPromptTemplate into a plain dict.

    Args:
        prompt_template: ChatPromptTemplate pulled from LangSmith Hub

    Returns:
        Dict with system_prompt, user_prompt and metadata fields
    """
    system_prompt = ""
    user_prompt = ""

    for message in prompt_template.messages:
        role = type(message).__name__
        template = message.prompt.template if hasattr(message, "prompt") else ""

        if "System" in role:
            system_prompt = template
        elif "Human" in role:
            user_prompt = template

    return {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories (baseline — baixa qualidade)",
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "version": "v1",
            "source": SOURCE_PROMPT,
            "tags": ["bug-analysis", "user-story", "baseline"],
        }
    }


def pull_prompts_from_langsmith() -> bool:
    """
    Pulls the baseline prompt from LangSmith Hub and saves it locally.

    Returns:
        True on success, False on failure
    """
    print_section_header("PULLING PROMPTS FROM LANGSMITH HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return False

    print(f"Source : {SOURCE_PROMPT}")
    print(f"Target : {LOCAL_FILE}\n")

    try:
        prompt_template = hub.pull(SOURCE_PROMPT)
        print(f"Pulled successfully — type: {type(prompt_template).__name__}")

        data = extract_prompt_data(prompt_template)

        if save_yaml(data, str(LOCAL_FILE)):
            print(f"Saved to {LOCAL_FILE}")
            return True
        else:
            print("Failed to save YAML file")
            return False

    except Exception as e:
        print(f"Error pulling prompt: {e}")
        return False


def main():
    """Main entry point."""
    success = pull_prompts_from_langsmith()

    if success:
        print("\nNext step: optimize the prompt and create prompts/bug_to_user_story_v2.yml")
        print("Then run: python src/push_prompts.py")
        return 0
    else:
        print("\nFailed to pull prompts. Check your .env credentials.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
