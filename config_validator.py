from typing import Dict, List, Tuple

class ConfigValidator:
    def __init__(self):
        self.rules = self._load_validation_rules()
    
    def validate_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """Validate configuration against rules"""
        errors = []
        warnings = []
        
        for section, rules in self.rules.items():
            section_result = self._validate_section(config.get(section, {}), rules)
            errors.extend(section_result.errors)
            warnings.extend(section_result.warnings)
            
        return len(errors) == 0, errors, warnings
