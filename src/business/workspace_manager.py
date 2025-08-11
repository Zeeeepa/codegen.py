"""
Workspace Manager Implementation

Handles multi-repository project workspaces as proposed in PR 9.
Provides workspace creation, switching, syncing, and repository management.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import subprocess
import shutil

from ..interfaces.business_logic import (
    IWorkspaceManager, Workspace, WorkspaceStatus
)
from ..interfaces.events import IEventBus, EventType, create_workspace_event

logger = logging.getLogger(__name__)


class WorkspaceManager(IWorkspaceManager):
    """
    Workspace manager for multi-repository projects.
    
    Implements the workspace management features proposed in PR 9,
    including workspace creation, switching, syncing, and repository management.
    """
    
    def __init__(self, event_bus: Optional[IEventBus] = None):
        """Initialize workspace manager"""
        self.event_bus = event_bus
        self.workspaces_dir = Path.home() / ".codegen" / "workspaces"
        self.config_file = Path.home() / ".codegen" / "workspace_config.json"
        self.current_workspace_file = Path.home() / ".codegen" / "current_workspace"
        
        # Ensure directories exist
        self.workspaces_dir.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self._load_config()
        
        logger.info("Initialized WorkspaceManager")
    
    def _load_config(self) -> None:
        """Load workspace configuration"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "default_workspace": "default",
                    "auto_sync": True,
                    "sync_timeout": 300,
                    "max_workspaces": 50
                }
                self._save_config()
        except Exception as e:
            logger.error(f"Failed to load workspace config: {e}")
            self.config = {}
    
    def _save_config(self) -> None:
        """Save workspace configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save workspace config: {e}")
    
    def _get_workspace_path(self, name: str) -> Path:
        """Get path for workspace directory"""
        return self.workspaces_dir / name
    
    def _get_workspace_config_path(self, name: str) -> Path:
        """Get path for workspace configuration file"""
        return self._get_workspace_path(name) / "workspace.json"
    
    def _load_workspace_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Load workspace configuration"""
        config_path = self._get_workspace_config_path(name)
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load workspace config for '{name}': {e}")
        return None
    
    def _save_workspace_config(self, name: str, config: Dict[str, Any]) -> None:
        """Save workspace configuration"""
        config_path = self._get_workspace_config_path(name)
        try:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save workspace config for '{name}': {e}")
    
    def _validate_workspace_name(self, name: str) -> List[str]:
        """Validate workspace name and return errors"""
        errors = []
        
        if not name:
            errors.append("Workspace name cannot be empty")
        
        if len(name) > 50:
            errors.append("Workspace name too long (max 50 characters)")
        
        # Check for invalid characters
        invalid_chars = set('<>:"/\\|?*')
        if any(c in invalid_chars for c in name):
            errors.append("Workspace name contains invalid characters")
        
        return errors
    
    def _validate_repository_url(self, repo_url: str) -> List[str]:
        """Validate repository URL and return errors"""
        errors = []
        
        if not repo_url:
            errors.append("Repository URL cannot be empty")
        
        # Basic URL validation
        if not (repo_url.startswith('http://') or 
                repo_url.startswith('https://') or 
                repo_url.startswith('git@')):
            errors.append("Invalid repository URL format")
        
        return errors
    
    def create_workspace(
        self,
        name: str,
        repositories: List[str],
        description: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> Workspace:
        """Create a new workspace"""
        
        # Validate inputs
        name_errors = self._validate_workspace_name(name)
        if name_errors:
            raise ValueError(f"Invalid workspace name: {', '.join(name_errors)}")
        
        for repo_url in repositories:
            repo_errors = self._validate_repository_url(repo_url)
            if repo_errors:
                raise ValueError(f"Invalid repository URL '{repo_url}': {', '.join(repo_errors)}")
        
        # Check if workspace already exists
        if self.get_workspace(name):
            raise ValueError(f"Workspace '{name}' already exists")
        
        # Create workspace directory
        workspace_path = self._get_workspace_path(name)
        workspace_path.mkdir(parents=True, exist_ok=True)
        
        # Create workspace configuration
        now = datetime.now()
        workspace_config = {
            "name": name,
            "description": description or "",
            "repositories": repositories,
            "status": WorkspaceStatus.ACTIVE.value,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "config": config or {},
            "metadata": {
                "created_by": "workspace_manager",
                "version": "1.0"
            }
        }
        
        # Save workspace configuration
        self._save_workspace_config(name, workspace_config)
        
        # Create workspace object
        workspace = Workspace(
            name=name,
            description=description or "",
            repositories=repositories,
            status=WorkspaceStatus.ACTIVE,
            created_at=now,
            updated_at=now,
            config=config or {},
            metadata=workspace_config["metadata"]
        )
        
        # Emit event
        if self.event_bus:
            event = create_workspace_event(
                EventType.WORKSPACE_CREATED,
                name,
                "workspace_manager",
                {"repositories": repositories, "description": description}
            )
            self.event_bus.publish(event)
        
        logger.info(f"Created workspace '{name}' with {len(repositories)} repositories")
        return workspace
    
    def get_workspace(self, name: str) -> Optional[Workspace]:
        """Get workspace by name"""
        config = self._load_workspace_config(name)
        if not config:
            return None
        
        try:
            return Workspace(
                name=config["name"],
                description=config.get("description", ""),
                repositories=config.get("repositories", []),
                status=WorkspaceStatus(config.get("status", WorkspaceStatus.ACTIVE.value)),
                created_at=datetime.fromisoformat(config["created_at"]),
                updated_at=datetime.fromisoformat(config["updated_at"]),
                config=config.get("config", {}),
                metadata=config.get("metadata", {})
            )
        except Exception as e:
            logger.error(f"Failed to parse workspace '{name}': {e}")
            return None
    
    def list_workspaces(self) -> List[Workspace]:
        """List all workspaces"""
        workspaces = []
        
        if not self.workspaces_dir.exists():
            return workspaces
        
        for workspace_dir in self.workspaces_dir.iterdir():
            if workspace_dir.is_dir():
                workspace = self.get_workspace(workspace_dir.name)
                if workspace:
                    workspaces.append(workspace)
        
        # Sort by name
        workspaces.sort(key=lambda w: w.name)
        return workspaces
    
    def switch_workspace(self, name: str) -> bool:
        """Switch to a different workspace"""
        workspace = self.get_workspace(name)
        if not workspace:
            logger.error(f"Workspace '{name}' not found")
            return False
        
        try:
            # Save current workspace
            with open(self.current_workspace_file, 'w') as f:
                f.write(name)
            
            # Emit event
            if self.event_bus:
                event = create_workspace_event(
                    EventType.WORKSPACE_SWITCHED,
                    name,
                    "workspace_manager"
                )
                self.event_bus.publish(event)
            
            logger.info(f"Switched to workspace '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch to workspace '{name}': {e}")
            return False
    
    def get_current_workspace(self) -> Optional[Workspace]:
        """Get currently active workspace"""
        try:
            if self.current_workspace_file.exists():
                with open(self.current_workspace_file, 'r') as f:
                    current_name = f.read().strip()
                    if current_name:
                        return self.get_workspace(current_name)
        except Exception as e:
            logger.error(f"Failed to get current workspace: {e}")
        
        # Return default workspace if no current workspace set
        default_name = self.config.get("default_workspace", "default")
        return self.get_workspace(default_name)
    
    def sync_workspace(self, name: str, force: bool = False) -> bool:
        """Sync workspace repositories"""
        workspace = self.get_workspace(name)
        if not workspace:
            logger.error(f"Workspace '{name}' not found")
            return False
        
        workspace_path = self._get_workspace_path(name)
        success_count = 0
        total_repos = len(workspace.repositories)
        
        logger.info(f"Syncing workspace '{name}' with {total_repos} repositories")
        
        for repo_url in workspace.repositories:
            try:
                repo_name = self._extract_repo_name(repo_url)
                repo_path = workspace_path / repo_name
                
                if repo_path.exists() and not force:
                    # Pull latest changes
                    result = subprocess.run(
                        ["git", "pull"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=self.config.get("sync_timeout", 300)
                    )
                    
                    if result.returncode == 0:
                        logger.debug(f"Pulled updates for {repo_name}")
                        success_count += 1
                    else:
                        logger.warning(f"Failed to pull {repo_name}: {result.stderr}")
                else:
                    # Clone repository
                    if repo_path.exists() and force:
                        shutil.rmtree(repo_path)
                    
                    result = subprocess.run(
                        ["git", "clone", repo_url, str(repo_path)],
                        capture_output=True,
                        text=True,
                        timeout=self.config.get("sync_timeout", 300)
                    )
                    
                    if result.returncode == 0:
                        logger.debug(f"Cloned {repo_name}")
                        success_count += 1
                    else:
                        logger.warning(f"Failed to clone {repo_name}: {result.stderr}")
                        
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout syncing repository: {repo_url}")
            except Exception as e:
                logger.error(f"Error syncing repository {repo_url}: {e}")
        
        # Update workspace status
        if success_count == total_repos:
            status = WorkspaceStatus.ACTIVE
        elif success_count > 0:
            status = WorkspaceStatus.ACTIVE  # Partial success still active
        else:
            status = WorkspaceStatus.ERROR
        
        self._update_workspace_status(name, status)
        
        # Emit event
        if self.event_bus:
            event = create_workspace_event(
                EventType.WORKSPACE_SYNCED,
                name,
                "workspace_manager",
                {"success_count": success_count, "total_repos": total_repos}
            )
            self.event_bus.publish(event)
        
        logger.info(f"Synced {success_count}/{total_repos} repositories for workspace '{name}'")
        return success_count > 0
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL"""
        # Handle different URL formats
        if repo_url.endswith('.git'):
            repo_url = repo_url[:-4]
        
        return repo_url.split('/')[-1]
    
    def _update_workspace_status(self, name: str, status: WorkspaceStatus) -> None:
        """Update workspace status"""
        config = self._load_workspace_config(name)
        if config:
            config["status"] = status.value
            config["updated_at"] = datetime.now().isoformat()
            self._save_workspace_config(name, config)
    
    def delete_workspace(self, name: str, force: bool = False) -> bool:
        """Delete a workspace"""
        workspace = self.get_workspace(name)
        if not workspace:
            logger.error(f"Workspace '{name}' not found")
            return False
        
        # Check if it's the current workspace
        current = self.get_current_workspace()
        if current and current.name == name and not force:
            logger.error(f"Cannot delete current workspace '{name}' without force flag")
            return False
        
        try:
            workspace_path = self._get_workspace_path(name)
            if workspace_path.exists():
                shutil.rmtree(workspace_path)
            
            # Switch to default workspace if deleting current
            if current and current.name == name:
                default_name = self.config.get("default_workspace", "default")
                if default_name != name:
                    self.switch_workspace(default_name)
            
            # Emit event
            if self.event_bus:
                event = create_workspace_event(
                    EventType.WORKSPACE_DELETED,
                    name,
                    "workspace_manager"
                )
                self.event_bus.publish(event)
            
            logger.info(f"Deleted workspace '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete workspace '{name}': {e}")
            return False
    
    def add_repository(self, workspace_name: str, repo_url: str) -> bool:
        """Add repository to workspace"""
        workspace = self.get_workspace(workspace_name)
        if not workspace:
            logger.error(f"Workspace '{workspace_name}' not found")
            return False
        
        # Validate repository URL
        repo_errors = self._validate_repository_url(repo_url)
        if repo_errors:
            logger.error(f"Invalid repository URL: {', '.join(repo_errors)}")
            return False
        
        # Check if repository already exists
        if repo_url in workspace.repositories:
            logger.warning(f"Repository already exists in workspace '{workspace_name}'")
            return True
        
        try:
            # Update workspace configuration
            config = self._load_workspace_config(workspace_name)
            if config:
                config["repositories"].append(repo_url)
                config["updated_at"] = datetime.now().isoformat()
                self._save_workspace_config(workspace_name, config)
                
                logger.info(f"Added repository to workspace '{workspace_name}': {repo_url}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add repository to workspace '{workspace_name}': {e}")
        
        return False
    
    def remove_repository(self, workspace_name: str, repo_url: str) -> bool:
        """Remove repository from workspace"""
        workspace = self.get_workspace(workspace_name)
        if not workspace:
            logger.error(f"Workspace '{workspace_name}' not found")
            return False
        
        if repo_url not in workspace.repositories:
            logger.warning(f"Repository not found in workspace '{workspace_name}'")
            return True
        
        try:
            # Update workspace configuration
            config = self._load_workspace_config(workspace_name)
            if config:
                config["repositories"].remove(repo_url)
                config["updated_at"] = datetime.now().isoformat()
                self._save_workspace_config(workspace_name, config)
                
                # Remove repository directory if it exists
                repo_name = self._extract_repo_name(repo_url)
                repo_path = self._get_workspace_path(workspace_name) / repo_name
                if repo_path.exists():
                    shutil.rmtree(repo_path)
                
                logger.info(f"Removed repository from workspace '{workspace_name}': {repo_url}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to remove repository from workspace '{workspace_name}': {e}")
        
        return False

