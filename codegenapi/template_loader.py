"""
Task template loader and processor
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import TemplateError
from .models import TaskTemplate


class TemplateLoader:
    """Loads and processes task templates"""
    
    def __init__(self, tasks_dir: str = "TASKS", config_file: str = "config.yaml"):
        self.tasks_dir = Path(tasks_dir)
        self.config_file = Path(config_file)
        self._templates = {}
        self._config = self._load_config()
        self._load_templates()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load task configuration"""
        if not self.config_file.exists():
            return {"tasks": {}}
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
                return config
        except Exception as e:
            raise TemplateError(f"Failed to load config: {e}")
    
    def _load_templates(self) -> None:
        """Load all task templates"""
        if not self.tasks_dir.exists():
            return
        
        task_mappings = self._config.get("tasks", {})
        
        for task_type, template_path in task_mappings.items():
            full_path = Path(template_path)
            if not full_path.is_absolute():
                full_path = self.tasks_dir.parent / template_path
            
            if full_path.exists():
                self._templates[task_type] = TaskTemplate(
                    name=task_type,
                    template_path=str(full_path),
                    description=f"Template for {task_type}",
                    variables=self._extract_variables(full_path)
                )
    
    def _extract_variables(self, template_path: Path) -> list[str]:
        """Extract template variables from file"""
        variables = []
        try:
            with open(template_path, 'r') as f:
                content = f.read()
                # Simple variable extraction - look for {{variable}} patterns
                import re
                matches = re.findall(r'\{\{(\w+)\}\}', content)
                variables = list(set(matches))
        except Exception:
            pass
        return variables
    
    def get_template(self, task_type: str) -> Optional[TaskTemplate]:
        """Get template by task type"""
        return self._templates.get(task_type)
    
    def list_templates(self) -> list[TaskTemplate]:
        """List all available templates"""
        return list(self._templates.values())
    
    def process_template(self, task_type: str, variables: Dict[str, Any]) -> str:
        """Process template with variables"""
        template = self.get_template(task_type)
        if not template:
            raise TemplateError(f"Template not found for task type: {task_type}")
        
        try:
            with open(template.template_path, 'r') as f:
                content = f.read()
            
            # Replace variables
            for var_name, var_value in variables.items():
                placeholder = f"{{{{{var_name}}}}}"
                content = content.replace(placeholder, str(var_value))
            
            return content
        except Exception as e:
            raise TemplateError(f"Failed to process template: {e}")
    
    def create_default_config(self) -> None:
        """Create default config.yaml file"""
        default_config = {
            "tasks": {
                "PLAN_CREATION": "TASKS/PLAN_CREATION.md",
                "CODE_RESTRUCTURE": "TASKS/CODE_RESTRUCTURE.md",
                "FEATURE_IMPLEMENTATION": "TASKS/FEATURE_IMPLEMENTATION.md",
                "BUG_FIX": "TASKS/BUG_FIX.md",
                "CODEBASE_ANALYSIS": "TASKS/CODEBASE_ANALYSIS.md",
                "TEST_GENERATION": "TASKS/TEST_GENERATION.md",
                "DOCUMENTATION_GENERATION": "TASKS/DOCUMENTATION_GENERATION.md"
            },
            "api": {
                "base_url": "https://codegen-sh-rest-api.modal.run",
                "timeout": 300
            },
            "storage": {
                "tasks_dir": "~/.codegenapi/tasks",
                "logs_dir": "~/.codegenapi/logs"
            }
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(default_config, f, default_flow_style=False)
        except Exception as e:
            raise TemplateError(f"Failed to create default config: {e}")

