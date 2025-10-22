"""
Prompt Loader Utility
Loads system prompts from configuration file for easy editing
"""

import json
import os
from typing import Dict, Any

class PromptLoader:
    """Load and manage system prompts from configuration"""

    def __init__(self, config_path: str = None):
        """Initialize prompt loader"""
        if config_path is None:
            # Default to config/prompts/system_prompts.json
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
            config_path = os.path.join(project_root, 'config/prompts/system_prompts.json')

        self.config_path = config_path
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """Load prompts from JSON file"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️  Warning: Prompts file not found at {self.config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"⚠️  Warning: Failed to parse prompts file: {e}")
            return {}

    def get_prompt(self, category: str, prompt_name: str) -> str:
        """Get a specific prompt template"""
        try:
            return self.prompts[category][prompt_name]['template']
        except KeyError:
            print(f"⚠️  Warning: Prompt not found: {category}.{prompt_name}")
            return ""

    def get_redirect(self, redirect_type: str) -> str:
        """Get a redirect response"""
        try:
            return self.prompts['redirects'][redirect_type]
        except KeyError:
            print(f"⚠️  Warning: Redirect not found: {redirect_type}")
            return "Tell me more about that."

    def reload(self):
        """Reload prompts from file (useful for live editing)"""
        self.prompts = self._load_prompts()
        print("✅ Prompts reloaded from config")

# Global instance for easy access
_prompt_loader = None

def get_prompt_loader() -> PromptLoader:
    """Get global prompt loader instance"""
    global _prompt_loader
    if _prompt_loader is None:
        _prompt_loader = PromptLoader()
    return _prompt_loader
