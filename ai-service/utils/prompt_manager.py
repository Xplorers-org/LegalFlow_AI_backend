import os
from jinja2 import Template


class PromptManager:
    """Externalized prompt manager loading and rendering Jinja2 template files."""

    def __init__(self, prompts_dir: str = None):
        if not prompts_dir:
            prompts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")
        self.prompts_dir = prompts_dir

    def load_prompt(self, template_name: str, **kwargs) -> str:
        """Loads prompt file from disk and renders Jinja2 keyword parameters."""
        file_path = os.path.join(self.prompts_dir, template_name)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Prompt template file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        template = Template(raw_text)
        return template.render(**kwargs)
