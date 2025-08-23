"""
Controller for the Codegen UI.

This module provides a controller for the Codegen UI, handling
communication between the UI and the API client.
"""

import logging
import threading
from typing import Dict, List, Any, Optional, Callable

from ui.core.events import EventBus, Event, EventType
from unified_backend import APIClient, Config, NotificationManager, Storage
from ui.utils.constants import EVENT_TYPES

logger = logging.getLogger(__name__)

class Controller:
    """
    Controller for the Codegen UI.
    
    This class handles communication between the UI and the API client,
    and manages application state.
    """
    
    def __init__(self, api_client=None):
        """
        Initialize the controller.
        
        Args:
            api_client: API client (optional)
        """
        self.config = Config()
        self.storage = Storage()
        self.notification_manager = NotificationManager()
        self.event_bus = EventBus()
        
        # Initialize API client
        if api_client:
            self.api_client = api_client
        else:
            api_token = self.config.get_api_token()
            if api_token:
                self.api_client = APIClient(self.config)
            else:
                self.api_client = None
        
        # Initialize state
        self.current_org_id = self.config.get_org_id()
        self.current_view = "agent_runs"
        self.current_agent_run_id = None
        self.current_project_id = None
        self.current_template_id = None
        
        # Start notification polling
        if self.api_client and self.current_org_id:
            self.notification_manager.start_polling(
                self.api_client,
                self.current_org_id
            )
    
    # Authentication
    
    def login(self, api_token: str) -> bool:
        """
        Log in to the API.
        
        Args:
            api_token: API token
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            # Initialize API client
            self.api_client = APIClient(self.config)
            
            # Test connection
            orgs = self.api_client.get_organizations()
            
            # Save API token
            self.config.set("api", "codegen_api_token", api_token)
            
            # Set current organization
            if orgs:
                self.current_org_id = orgs[0].get("id")
                self.config.set("api", "codegen_org_id", self.current_org_id)
            
            # Start notification polling
            if self.current_org_id:
                self.notification_manager.start_polling(
                    self.api_client,
                    self.current_org_id
                )
            
            # Fire login event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["LOGIN"],
                data={}
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            self.api_client = None
            return False
    
    def logout(self) -> bool:
        """
        Log out from the API.
        
        Returns:
            True if logout successful, False otherwise
        """
        try:
            # Clear API token
            self.config.set("api", "codegen_api_token", "")
            
            # Clear current organization
            self.current_org_id = None
            self.config.set("api", "codegen_org_id", "")
            
            # Clear API client
            self.api_client = None
            
            # Fire logout event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["LOGOUT"],
                data={}
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False
    
    def is_logged_in(self) -> bool:
        """
        Check if logged in.
        
        Returns:
            True if logged in, False otherwise
        """
        return self.api_client is not None
    
    # Agent runs
    
    def get_agent_runs(self) -> List[Dict[str, Any]]:
        """
        Get agent runs.
        
        Returns:
            List of agent runs
        """
        if not self.api_client or not self.current_org_id:
            return []
        
        try:
            response = self.api_client.list_agent_runs(self.current_org_id)
            return response.get("items", [])
        except Exception as e:
            logger.error(f"Error getting agent runs: {e}")
            return []
    
    def get_agent_run(self, agent_run_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            Agent run or None if not found
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            return self.api_client.get_agent_run(self.current_org_id, agent_run_id)
        except Exception as e:
            logger.error(f"Error getting agent run: {e}")
            return None
    
    def get_agent_run_logs(self, agent_run_id: str) -> List[Dict[str, Any]]:
        """
        Get agent run logs.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            List of agent run logs
        """
        if not self.api_client or not self.current_org_id:
            return []
        
        try:
            response = self.api_client.get_agent_run_logs(self.current_org_id, agent_run_id)
            return response.get("logs", [])
        except Exception as e:
            logger.error(f"Error getting agent run logs: {e}")
            return []
    
    def get_agent_run_tools_used(self, agent_run_id: str) -> List[Dict[str, Any]]:
        """
        Get agent run tools used.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            List of agent run tools used
        """
        # This is a placeholder - the API doesn't currently provide this information
        return []
    
    def get_agent_run_timeline(self, agent_run_id: str) -> List[Dict[str, Any]]:
        """
        Get agent run timeline.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            List of agent run timeline events
        """
        # This is a placeholder - the API doesn't currently provide this information
        return []
    
    def create_agent_run(
        self, 
        prompt: str,
        model: Optional[str] = None,
        repo_id: Optional[str] = None,
        prorun: bool = False,
        candidates: int = 10,
        agent_models: Optional[List[str]] = None,
        synthesis_template: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create agent run.
        
        Args:
            prompt: Prompt text
            model: Model to use
            repo_id: Repository ID
            prorun: Whether to use ProRun mode
            candidates: Number of candidates for ProRun mode
            agent_models: List of agent models for ProRun mode
            synthesis_template: Synthesis template for ProRun mode
            
        Returns:
            Created agent run or None if creation failed
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            agent_run = self.api_client.create_agent_run(
                self.current_org_id,
                prompt,
                model,
                repo_id,
                prorun,
                candidates,
                agent_models,
                synthesis_template
            )
            
            # Fire agent run created event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["AGENT_RUN_CREATED"],
                data={
                    "agent_run_id": agent_run.get("id")
                }
            ))
            
            return agent_run
        except Exception as e:
            logger.error(f"Error creating agent run: {e}")
            return None
    
    def resume_agent_run(self, agent_run_id: str) -> bool:
        """
        Resume agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            True if resume successful, False otherwise
        """
        if not self.api_client or not self.current_org_id:
            return False
        
        try:
            self.api_client.resume_agent_run(self.current_org_id, agent_run_id)
            
            # Fire agent run resumed event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["AGENT_RUN_RESUMED"],
                data={
                    "agent_run_id": agent_run_id
                }
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error resuming agent run: {e}")
            return False
    
    def stop_agent_run(self, agent_run_id: str) -> bool:
        """
        Stop agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            True if stop successful, False otherwise
        """
        # This is a placeholder - the API doesn't currently provide this functionality
        return False
    
    def ban_all_checks_for_agent_run(self, agent_run_id: str) -> bool:
        """
        Ban all checks for agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            True if ban successful, False otherwise
        """
        if not self.api_client or not self.current_org_id:
            return False
        
        try:
            self.api_client.ban_all_checks_for_agent_run(self.current_org_id, agent_run_id)
            return True
        except Exception as e:
            logger.error(f"Error banning all checks for agent run: {e}")
            return False
    
    def unban_all_checks_for_agent_run(self, agent_run_id: str) -> bool:
        """
        Unban all checks for agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            True if unban successful, False otherwise
        """
        if not self.api_client or not self.current_org_id:
            return False
        
        try:
            self.api_client.unban_all_checks_for_agent_run(self.current_org_id, agent_run_id)
            return True
        except Exception as e:
            logger.error(f"Error unbanning all checks for agent run: {e}")
            return False
    
    def remove_codegen_from_pr(self, agent_run_id: str) -> bool:
        """
        Remove Codegen from PR.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            True if removal successful, False otherwise
        """
        if not self.api_client or not self.current_org_id:
            return False
        
        try:
            self.api_client.remove_codegen_from_pr(self.current_org_id, agent_run_id)
            return True
        except Exception as e:
            logger.error(f"Error removing Codegen from PR: {e}")
            return False
    
    # Starred runs
    
    def get_starred_agent_runs(self) -> List[str]:
        """
        Get starred agent runs.
        
        Returns:
            List of starred agent run IDs
        """
        if not self.api_client or not self.current_org_id:
            return []
        
        try:
            starred_runs = self.storage.load("starred_runs", [])
            return starred_runs
        except Exception as e:
            logger.error(f"Error getting starred agent runs: {e}")
            return []
    
    def star_agent_run(self, agent_run_id: str) -> bool:
        """
        Star agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            True if star successful, False otherwise
        """
        try:
            starred_runs = self.storage.load("starred_runs", [])
            
            if agent_run_id not in starred_runs:
                starred_runs.append(agent_run_id)
                self.storage.save("starred_runs", starred_runs)
            
            # Fire agent run starred event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["AGENT_RUN_STARRED"],
                data={
                    "agent_run_id": agent_run_id
                }
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error starring agent run: {e}")
            return False
    
    def unstar_agent_run(self, agent_run_id: str) -> bool:
        """
        Unstar agent run.
        
        Args:
            agent_run_id: Agent run ID
            
        Returns:
            True if unstar successful, False otherwise
        """
        try:
            starred_runs = self.storage.load("starred_runs", [])
            
            if agent_run_id in starred_runs:
                starred_runs.remove(agent_run_id)
                self.storage.save("starred_runs", starred_runs)
            
            # Fire agent run unstarred event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["AGENT_RUN_UNSTARRED"],
                data={
                    "agent_run_id": agent_run_id
                }
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error unstarring agent run: {e}")
            return False
    
    # Projects
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get projects.
        
        Returns:
            List of projects
        """
        if not self.api_client or not self.current_org_id:
            return []
        
        try:
            return self.api_client.get_repositories(self.current_org_id)
        except Exception as e:
            logger.error(f"Error getting projects: {e}")
            return []
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project or None if not found
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            projects = self.api_client.get_repositories(self.current_org_id)
            for project in projects:
                if project.get("id") == project_id:
                    return project
            return None
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return None
    
    def get_starred_projects(self) -> List[str]:
        """
        Get starred projects.
        
        Returns:
            List of starred project IDs
        """
        try:
            starred_projects = self.storage.load("starred_projects", [])
            return starred_projects
        except Exception as e:
            logger.error(f"Error getting starred projects: {e}")
            return []
    
    def star_project(self, project_id: str) -> bool:
        """
        Star project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if star successful, False otherwise
        """
        try:
            starred_projects = self.storage.load("starred_projects", [])
            
            if project_id not in starred_projects:
                starred_projects.append(project_id)
                self.storage.save("starred_projects", starred_projects)
            
            # Fire project starred event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["PROJECT_STARRED"],
                data={
                    "project_id": project_id
                }
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error starring project: {e}")
            return False
    
    def unstar_project(self, project_id: str) -> bool:
        """
        Unstar project.
        
        Args:
            project_id: Project ID
            
        Returns:
            True if unstar successful, False otherwise
        """
        try:
            starred_projects = self.storage.load("starred_projects", [])
            
            if project_id in starred_projects:
                starred_projects.remove(project_id)
                self.storage.save("starred_projects", starred_projects)
            
            # Fire project unstarred event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["PROJECT_UNSTARRED"],
                data={
                    "project_id": project_id
                }
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error unstarring project: {e}")
            return False
    
    def get_setup_commands(self) -> Dict[str, Dict[str, Any]]:
        """
        Get setup commands.
        
        Returns:
            Dictionary of project ID to setup commands
        """
        try:
            setup_commands = self.storage.load("setup_commands", {})
            return setup_commands
        except Exception as e:
            logger.error(f"Error getting setup commands: {e}")
            return {}
    
    def generate_setup_commands(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Generate setup commands.
        
        Args:
            project_id: Project ID
            
        Returns:
            Setup commands or None if generation failed
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            setup_commands = self.api_client.generate_setup_commands(
                self.current_org_id,
                project_id
            )
            
            # Save setup commands
            all_setup_commands = self.storage.load("setup_commands", {})
            all_setup_commands[project_id] = setup_commands
            self.storage.save("setup_commands", all_setup_commands)
            
            return setup_commands
        except Exception as e:
            logger.error(f"Error generating setup commands: {e}")
            return None
    
    # Templates
    
    def get_templates(self) -> List[Dict[str, Any]]:
        """
        Get templates.
        
        Returns:
            List of templates
        """
        if not self.api_client or not self.current_org_id:
            return []
        
        try:
            return self.api_client.get_templates(self.current_org_id)
        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            return []
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Template or None if not found
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            return self.api_client.get_template(self.current_org_id, template_id)
        except Exception as e:
            logger.error(f"Error getting template: {e}")
            return None
    
    def create_template(
        self, 
        name: str, 
        content: str, 
        category: str, 
        description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create template.
        
        Args:
            name: Template name
            content: Template content
            category: Template category
            description: Template description
            
        Returns:
            Created template or None if creation failed
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            template = self.api_client.create_template(
                self.current_org_id,
                name,
                content,
                category,
                description
            )
            
            # Fire template created event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["TEMPLATE_CREATED"],
                data={
                    "template_id": template.get("id")
                }
            ))
            
            return template
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            return None
    
    def update_template(
        self, 
        template_id: str, 
        name: str, 
        content: str, 
        category: str, 
        description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update template.
        
        Args:
            template_id: Template ID
            name: Template name
            content: Template content
            category: Template category
            description: Template description
            
        Returns:
            Updated template or None if update failed
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            template = self.api_client.update_template(
                self.current_org_id,
                template_id,
                name,
                content,
                category,
                description
            )
            
            # Fire template updated event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["TEMPLATE_UPDATED"],
                data={
                    "template_id": template_id
                }
            ))
            
            return template
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return None
    
    def delete_template(self, template_id: str) -> bool:
        """
        Delete template.
        
        Args:
            template_id: Template ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.api_client or not self.current_org_id:
            return False
        
        try:
            self.api_client.delete_template(self.current_org_id, template_id)
            
            # Fire template deleted event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["TEMPLATE_DELETED"],
                data={
                    "template_id": template_id
                }
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return False
    
    # ProRun configurations
    
    def get_prorun_configurations(self) -> List[Dict[str, Any]]:
        """
        Get ProRun configurations.
        
        Returns:
            List of ProRun configurations
        """
        if not self.api_client or not self.current_org_id:
            return []
        
        try:
            return self.api_client.get_prorun_configurations(self.current_org_id)
        except Exception as e:
            logger.error(f"Error getting ProRun configurations: {e}")
            return []
    
    def get_prorun_configuration(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Get ProRun configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            ProRun configuration or None if not found
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            return self.api_client.get_prorun_configuration(self.current_org_id, config_id)
        except Exception as e:
            logger.error(f"Error getting ProRun configuration: {e}")
            return None
    
    def create_prorun_configuration(
        self, 
        name: str, 
        description: str, 
        candidates: int, 
        agent_models: List[str], 
        synthesis_template: str
    ) -> Optional[Dict[str, Any]]:
        """
        Create ProRun configuration.
        
        Args:
            name: Configuration name
            description: Configuration description
            candidates: Number of candidates
            agent_models: List of agent models
            synthesis_template: Synthesis template
            
        Returns:
            Created ProRun configuration or None if creation failed
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            config = self.api_client.create_prorun_configuration(
                self.current_org_id,
                name,
                description,
                candidates,
                agent_models,
                synthesis_template
            )
            
            # Fire ProRun configuration created event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["PRORUN_CONFIG_CREATED"],
                data={
                    "config_id": config.get("id")
                }
            ))
            
            return config
        except Exception as e:
            logger.error(f"Error creating ProRun configuration: {e}")
            return None
    
    def update_prorun_configuration(
        self, 
        config_id: str, 
        name: str, 
        description: str, 
        candidates: int, 
        agent_models: List[str], 
        synthesis_template: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update ProRun configuration.
        
        Args:
            config_id: Configuration ID
            name: Configuration name
            description: Configuration description
            candidates: Number of candidates
            agent_models: List of agent models
            synthesis_template: Synthesis template
            
        Returns:
            Updated ProRun configuration or None if update failed
        """
        if not self.api_client or not self.current_org_id:
            return None
        
        try:
            config = self.api_client.update_prorun_configuration(
                self.current_org_id,
                config_id,
                name,
                description,
                candidates,
                agent_models,
                synthesis_template
            )
            
            # Fire ProRun configuration updated event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["PRORUN_CONFIG_UPDATED"],
                data={
                    "config_id": config_id
                }
            ))
            
            return config
        except Exception as e:
            logger.error(f"Error updating ProRun configuration: {e}")
            return None
    
    def delete_prorun_configuration(self, config_id: str) -> bool:
        """
        Delete ProRun configuration.
        
        Args:
            config_id: Configuration ID
            
        Returns:
            True if deletion successful, False otherwise
        """
        if not self.api_client or not self.current_org_id:
            return False
        
        try:
            self.api_client.delete_prorun_configuration(self.current_org_id, config_id)
            
            # Fire ProRun configuration deleted event
            self.event_bus.publish(Event(
                type=EVENT_TYPES["PRORUN_CONFIG_DELETED"],
                data={
                    "config_id": config_id
                }
            ))
            
            return True
        except Exception as e:
            logger.error(f"Error deleting ProRun configuration: {e}")
            return False
    
    # Navigation
    
    def show_agent_runs(self):
        """Show agent runs view."""
        self.current_view = "agent_runs"
        self.current_agent_run_id = None
        self.current_project_id = None
        self.current_template_id = None
    
    def show_starred_runs(self):
        """Show starred runs view."""
        self.current_view = "starred_runs"
        self.current_agent_run_id = None
        self.current_project_id = None
        self.current_template_id = None
    
    def show_projects(self):
        """Show projects view."""
        self.current_view = "projects"
        self.current_agent_run_id = None
        self.current_project_id = None
        self.current_template_id = None
    
    def show_templates(self):
        """Show templates view."""
        self.current_view = "templates"
        self.current_agent_run_id = None
        self.current_project_id = None
        self.current_template_id = None
    
    def show_settings(self):
        """Show settings view."""
        self.current_view = "settings"
        self.current_agent_run_id = None
        self.current_project_id = None
        self.current_template_id = None
    
    def show_agent_run_detail(self, agent_run_id: str):
        """
        Show agent run detail view.
        
        Args:
            agent_run_id: Agent run ID
        """
        self.current_view = "agent_run_detail"
        self.current_agent_run_id = agent_run_id
        self.current_project_id = None
        self.current_template_id = None
    
    def show_project_detail(self, project_id: str):
        """
        Show project detail view.
        
        Args:
            project_id: Project ID
        """
        self.current_view = "project_detail"
        self.current_agent_run_id = None
        self.current_project_id = project_id
        self.current_template_id = None
    
    def show_template_detail(self, template_id: str):
        """
        Show template detail view.
        
        Args:
            template_id: Template ID
        """
        self.current_view = "template_detail"
        self.current_agent_run_id = None
        self.current_project_id = None
        self.current_template_id = template_id
    
    def show_create_agent_run_dialog(
        self, 
        project_id: Optional[str] = None,
        template_id: Optional[str] = None
    ):
        """
        Show create agent run dialog.
        
        Args:
            project_id: Project ID (optional)
            template_id: Template ID (optional)
        """
        # This is a placeholder - the UI will implement this
        pass
    
    def show_create_template_dialog(self):
        """Show create template dialog."""
        # This is a placeholder - the UI will implement this
        pass
    
    def show_edit_template_dialog(self, template_id: str):
        """
        Show edit template dialog.
        
        Args:
            template_id: Template ID
        """
        # This is a placeholder - the UI will implement this
        pass
    
    # Refresh
    
    def refresh(self):
        """Refresh current view."""
        # Fire refresh requested event
        self.event_bus.publish(Event(
            type=EVENT_TYPES["REFRESH_REQUESTED"],
            data={}
        ))

