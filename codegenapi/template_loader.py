"""
Template Loader

Loads and processes task templates from the TASKS folder.
Handles template rendering with variable substitution.
"""

import logging
from typing import Dict, Any, List
from pathlib import Path

from .models import Template, TaskType
from .exceptions import TemplateError, TemplateNotFoundError, TemplateRenderError

logger = logging.getLogger(__name__)


class TemplateLoader:
    """
    Template loader for task templates.
    
    Loads templates from the TASKS directory and provides rendering
    capabilities with variable substitution.
    """
    
    def __init__(self, tasks_dir: Path):
        """Initialize template loader"""
        self.tasks_dir = Path(tasks_dir)
        self._template_cache: Dict[TaskType, Template] = {}
        
        # Ensure tasks directory exists
        if not self.tasks_dir.exists():
            logger.warning(f"Tasks directory does not exist: {self.tasks_dir}")
        
        logger.info(f"Initialized TemplateLoader with directory: {self.tasks_dir}")
    
    def load_template(self, task_type: TaskType) -> Template:
        """Load template for task type"""
        
        # Check cache first
        if task_type in self._template_cache:
            return self._template_cache[task_type]
        
        # Load from file
        template_file = self.tasks_dir / f"{task_type.value}.md"
        
        if not template_file.exists():
            raise TemplateNotFoundError(f"Template file not found: {template_file}", task_type.value)
        
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse template
            template = self._parse_template(task_type, content)
            
            # Cache template
            self._template_cache[task_type] = template
            
            logger.debug(f"Loaded template for {task_type.value}")
            return template
            
        except Exception as e:
            logger.error(f"Failed to load template {task_type.value}: {e}")
            raise TemplateError(f"Failed to load template {task_type.value}: {e}", task_type.value)
    
    def list_available_templates(self) -> List[TaskType]:
        """List all available templates"""
        available = []
        
        if not self.tasks_dir.exists():
            return available
        
        for task_type in TaskType:
            template_file = self.tasks_dir / f"{task_type.value}.md"
            if template_file.exists():
                available.append(task_type)
        
        return available
    
    def reload_templates(self) -> None:
        """Reload all templates from disk"""
        self._template_cache.clear()
        logger.info("Template cache cleared")
    
    def _parse_template(self, task_type: TaskType, content: str) -> Template:
        """Parse template content and extract metadata"""
        
        lines = content.split('\n')
        description = ""
        variables = []
        template_content = content
        
        # Look for metadata in comments at the top
        in_metadata = False
        metadata_lines = []
        content_start = 0
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            if stripped.startswith('<!--') and 'TEMPLATE METADATA' in stripped:
                in_metadata = True
                continue
            elif stripped == '-->' and in_metadata:
                in_metadata = False
                content_start = i + 1
                break
            elif in_metadata:
                metadata_lines.append(stripped)
        
        # Parse metadata
        for line in metadata_lines:
            if line.startswith('Description:'):
                description = line.replace('Description:', '').strip()
            elif line.startswith('Variables:'):
                var_list = line.replace('Variables:', '').strip()
                if var_list:
                    variables = [v.strip() for v in var_list.split(',')]
        
        # Extract actual template content (skip metadata)
        if content_start > 0:
            template_content = '\n'.join(lines[content_start:])
        
        # Extract variables from template content if not in metadata
        if not variables:
            variables = self._extract_variables(template_content)
        
        # Use task type as description if none provided
        if not description:
            description = f"Template for {task_type.value.replace('_', ' ').title()}"
        
        return Template(
            name=task_type.value,
            task_type=task_type,
            content=template_content,
            description=description,
            variables=variables
        )
    
    def _extract_variables(self, content: str) -> List[str]:
        """Extract template variables from content"""
        import re
        
        # Find all {variable} patterns
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, content)
        
        # Remove duplicates and sort
        variables = sorted(list(set(matches)))
        
        return variables
    
    def validate_template(self, template: Template, variables: Dict[str, Any]) -> List[str]:
        """Validate template variables"""
        errors = []
        
        # Check for missing required variables
        for var in template.variables:
            if var not in variables:
                errors.append(f"Missing required variable: {var}")
        
        # Check for unknown variables in the provided dict
        template_vars = set(template.variables)
        provided_vars = set(variables.keys())
        unknown_vars = provided_vars - template_vars
        
        if unknown_vars:
            logger.warning(f"Unknown variables provided: {', '.join(unknown_vars)}")
        
        return errors
    
    def render_template(
        self,
        task_type: TaskType,
        variables: Dict[str, Any]
    ) -> str:
        """Render template with variables"""
        
        template = self.load_template(task_type)
        
        # Validate variables
        errors = self.validate_template(template, variables)
        if errors:
            raise TemplateRenderError(f"Template validation failed: {'; '.join(errors)}", task_type.value)
        
        try:
            return template.render(variables)
        except Exception as e:
            logger.error(f"Failed to render template {task_type.value}: {e}")
            raise TemplateRenderError(f"Failed to render template {task_type.value}: {e}", task_type.value)

