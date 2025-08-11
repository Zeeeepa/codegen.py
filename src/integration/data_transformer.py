"""
Data Transformer Implementation

Handles conversion between API responses and internal data models.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime

from ..interfaces.codegen_integration import (
    IDataTransformer, AgentRun, Organization, User, AgentRunLog, 
    PaginatedResponse, SourceType, RunStatus
)

logger = logging.getLogger(__name__)


class DataTransformer(IDataTransformer):
    """
    Data transformer for converting API responses to internal data models.
    
    Handles type conversion, validation, and default value assignment.
    """
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API response"""
        if not date_str:
            return None
        
        try:
            # Handle different datetime formats
            formats = [
                "%Y-%m-%dT%H:%M:%S.%fZ",  # ISO format with microseconds
                "%Y-%m-%dT%H:%M:%SZ",     # ISO format without microseconds
                "%Y-%m-%dT%H:%M:%S.%f",   # ISO format without Z
                "%Y-%m-%dT%H:%M:%S",      # ISO format basic
                "%Y-%m-%d %H:%M:%S",      # Space separated
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            logger.warning(f"Unable to parse datetime: {date_str}")
            return None
            
        except Exception as e:
            logger.warning(f"Error parsing datetime '{date_str}': {e}")
            return None
    
    def _parse_source_type(self, source_type_str: Optional[str]) -> Optional[SourceType]:
        """Parse source type from string"""
        if not source_type_str:
            return None
        
        try:
            return SourceType(source_type_str)
        except ValueError:
            logger.warning(f"Unknown source type: {source_type_str}")
            return None
    
    def _parse_run_status(self, status_str: Optional[str]) -> Optional[RunStatus]:
        """Parse run status from string"""
        if not status_str:
            return None
        
        # Map common status variations
        status_mapping = {
            "ACTIVE": RunStatus.ACTIVE,
            "COMPLETE": RunStatus.COMPLETE,
            "COMPLETED": RunStatus.COMPLETE,
            "PENDING": RunStatus.PENDING,
            "FAILED": RunStatus.FAILED,
            "ERROR": RunStatus.FAILED,
            "CANCELLED": RunStatus.CANCELLED,
            "CANCELED": RunStatus.CANCELLED,
            "PAUSED": RunStatus.PAUSED
        }
        
        normalized_status = status_str.upper()
        status = status_mapping.get(normalized_status)
        
        if not status:
            logger.warning(f"Unknown run status: {status_str}")
            # Try direct enum conversion as fallback
            try:
                status = RunStatus(status_str)
            except ValueError:
                pass
        
        return status
    
    def transform_agent_run(self, api_data: Dict[str, Any]) -> AgentRun:
        """Transform API response to AgentRun model"""
        try:
            return AgentRun(
                id=api_data.get("id", 0),
                organization_id=api_data.get("organization_id", 0),
                status=self._parse_run_status(api_data.get("status")),
                prompt=api_data.get("prompt"),
                result=api_data.get("result"),
                created_at=self._parse_datetime(api_data.get("created_at")),
                updated_at=self._parse_datetime(api_data.get("updated_at")),
                completed_at=self._parse_datetime(api_data.get("completed_at")),
                web_url=api_data.get("web_url"),
                source_type=self._parse_source_type(api_data.get("source_type")),
                metadata=api_data.get("metadata", {}),
                github_pull_requests=api_data.get("github_pull_requests", []),
                cost=float(api_data.get("cost", 0.0)) if api_data.get("cost") is not None else 0.0,
                tokens_used=int(api_data.get("tokens_used", 0)) if api_data.get("tokens_used") is not None else 0,
                progress=self._calculate_progress(api_data.get("status"))
            )
        except Exception as e:
            logger.error(f"Error transforming agent run data: {e}")
            logger.debug(f"API data: {api_data}")
            raise
    
    def _calculate_progress(self, status: Optional[str]) -> int:
        """Calculate progress percentage based on status"""
        if not status:
            return 0
        
        status_progress = {
            "PENDING": 0,
            "ACTIVE": 50,
            "COMPLETE": 100,
            "COMPLETED": 100,
            "FAILED": 0,
            "ERROR": 0,
            "CANCELLED": 0,
            "CANCELED": 0,
            "PAUSED": 25
        }
        
        return status_progress.get(status.upper(), 0)
    
    def transform_organization(self, api_data: Dict[str, Any]) -> Organization:
        """Transform API response to Organization model"""
        try:
            return Organization(
                id=api_data.get("id", 0),
                name=api_data.get("name", ""),
                settings=api_data.get("settings", {})
            )
        except Exception as e:
            logger.error(f"Error transforming organization data: {e}")
            logger.debug(f"API data: {api_data}")
            raise
    
    def transform_user(self, api_data: Dict[str, Any]) -> User:
        """Transform API response to User model"""
        try:
            return User(
                id=api_data.get("id", 0),
                email=api_data.get("email"),
                github_user_id=api_data.get("github_user_id", ""),
                github_username=api_data.get("github_username", ""),
                avatar_url=api_data.get("avatar_url"),
                full_name=api_data.get("full_name")
            )
        except Exception as e:
            logger.error(f"Error transforming user data: {e}")
            logger.debug(f"API data: {api_data}")
            raise
    
    def transform_agent_run_log(self, api_data: Dict[str, Any]) -> AgentRunLog:
        """Transform API response to AgentRunLog model"""
        try:
            return AgentRunLog(
                agent_run_id=api_data.get("agent_run_id", 0),
                created_at=self._parse_datetime(api_data.get("created_at")) or datetime.now(),
                message_type=api_data.get("message_type", ""),
                thought=api_data.get("thought"),
                tool_name=api_data.get("tool_name"),
                tool_input=api_data.get("tool_input"),
                tool_output=api_data.get("tool_output"),
                observation=api_data.get("observation")
            )
        except Exception as e:
            logger.error(f"Error transforming agent run log data: {e}")
            logger.debug(f"API data: {api_data}")
            raise
    
    def transform_paginated_response(
        self, 
        api_data: Dict[str, Any], 
        item_transformer: Callable[[Dict[str, Any]], Any]
    ) -> PaginatedResponse:
        """Transform paginated API response"""
        try:
            items_data = api_data.get("items", [])
            transformed_items = []
            
            for item_data in items_data:
                try:
                    transformed_item = item_transformer(item_data)
                    transformed_items.append(transformed_item)
                except Exception as e:
                    logger.warning(f"Failed to transform item: {e}")
                    # Continue with other items
                    continue
            
            return PaginatedResponse(
                items=transformed_items,
                total=api_data.get("total", len(transformed_items)),
                page=api_data.get("page", 1),
                size=api_data.get("size", len(transformed_items)),
                pages=api_data.get("pages", 1)
            )
        except Exception as e:
            logger.error(f"Error transforming paginated response: {e}")
            logger.debug(f"API data: {api_data}")
            raise
    
    def transform_github_pull_request(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform GitHub pull request data"""
        return {
            "id": api_data.get("id"),
            "title": api_data.get("title"),
            "url": api_data.get("url"),
            "created_at": api_data.get("created_at"),
            "number": api_data.get("number"),
            "state": api_data.get("state"),
            "merged": api_data.get("merged", False)
        }
    
    def validate_agent_run_data(self, data: Dict[str, Any]) -> List[str]:
        """Validate agent run data and return list of errors"""
        errors = []
        
        if not data.get("id"):
            errors.append("Missing required field: id")
        
        if not data.get("organization_id"):
            errors.append("Missing required field: organization_id")
        
        if data.get("cost") is not None:
            try:
                float(data["cost"])
            except (ValueError, TypeError):
                errors.append("Invalid cost value: must be a number")
        
        if data.get("tokens_used") is not None:
            try:
                int(data["tokens_used"])
            except (ValueError, TypeError):
                errors.append("Invalid tokens_used value: must be an integer")
        
        return errors

