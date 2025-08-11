"""
CLI Router - Main entry point

Routes commands to appropriate handlers while maintaining clean separation
between CLI interface and Codegen API integration.
"""

import sys
import logging
from typing import List, Optional

from .cli import parse_arguments
from .config import Config
from .codegen_client import CodegenClient
from .task_manager import TaskManager
from .exceptions import CodegenError, TaskError
from .commands import new, resume, status


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main(args: Optional[List[str]] = None) -> int:
    """Main CLI entry point"""
    try:
        # Parse command line arguments
        parsed_args = parse_arguments(args or sys.argv[1:])
        
        # Setup logging
        setup_logging(parsed_args.log_level)
        logger = logging.getLogger(__name__)
        
        # Load configuration
        config = Config()
        
        # Initialize Codegen client
        client = CodegenClient(
            token=config.api_token,
            org_id=config.org_id,
            base_url=config.base_url
        )
        
        # Initialize task manager
        task_manager = TaskManager(client, config)
        
        # Route to appropriate command handler
        if parsed_args.command == "new":
            return new.handle(parsed_args, task_manager)
        elif parsed_args.command == "resume":
            return resume.handle(parsed_args, task_manager)
        elif parsed_args.command == "status":
            return status.handle(parsed_args, task_manager)
        else:
            logger.error(f"Unknown command: {parsed_args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        return 130
    except CodegenError as e:
        print(f"Codegen API Error: {e}")
        return 1
    except TaskError as e:
        print(f"Task Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.getLogger(__name__).exception("Unexpected error occurred")
        return 1


if __name__ == "__main__":
    sys.exit(main())

