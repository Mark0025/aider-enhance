# New main configuration manager
import os
import yaml
import inquirer
from rich.console import Console
from rich import print as rprint
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class ConfigurationMode(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    EXPERT = "expert"

@dataclass
class AiderConfig:
    """Configuration container with validation"""
    model_settings: Dict[str, Any]
    git_settings: Dict[str, Any]
    performance_settings: Dict[str, Any]
    output_settings: Dict[str, Any]
    test_settings: Dict[str, Any]
    voice_settings: Dict[str, Any]

class AiderConfigManager:
    def __init__(self):
        self.console = Console()
        self.config = self._load_default_config()
        self.ai_assistant = AIConfigAssistant()  # New AI assistant class
        
    def interactive_setup(self):
        """Main interactive configuration flow"""
        self.show_welcome()
        mode = self.get_configuration_mode()
        
        if mode == ConfigurationMode.BASIC:
            self.basic_setup()
        elif mode == ConfigurationMode.ADVANCED:
            self.advanced_setup()
        else:
            self.expert_setup()
            
        self.ai_review_and_optimize()
        self.save_configuration()

    def ai_review_and_optimize(self):
        """Have AI review and suggest optimizations"""
        suggestions = self.ai_assistant.analyze_config(self.config)
        if suggestions:
            self.show_ai_suggestions(suggestions)
