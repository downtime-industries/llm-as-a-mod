"""
Prompt templates for LLM-as-a-mod Discord bot
"""

from pathlib import Path

# Path to the prompts directory
PROMPTS_DIR = Path(__file__).parent

def load_prompt(prompt_name):
    """
    Load a prompt from the prompts directory
    
    Args:
        prompt_name: Name of the prompt file (without extension)
        
    Returns:
        The prompt text as a string
    """
    prompt_path = PROMPTS_DIR / f"{prompt_name}.txt"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file {prompt_name}.txt not found")
    
    with open(prompt_path, "r") as f:
        return f.read()

# Dictionary of available prompts
AVAILABLE_PROMPTS = {
    "code_of_conduct": "Evaluates messages against the community Code of Conduct"
}

# Export common prompts directly
CODE_OF_CONDUCT = load_prompt("code_of_conduct")