"""
Base tool abstract class for all AI tools in the system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import time
from functools import wraps

logger = logging.getLogger(__name__)


def retry_on_error(max_retries: int = 3, delay: int = 5):
    """
    Decorator for retrying function calls on error.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay in seconds between retries
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for {func.__name__}: {str(e)}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(delay * (attempt + 1))  # Exponential backoff
            
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_exception
        return wrapper
    return decorator


class BaseTool(ABC):
    """
    Abstract base class for all tools in the multi-agent system.
    
    All tools must implement:
    - execute(): Main execution logic
    - validate_input(): Input validation
    - handle_error(): Error handling logic
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize the base tool.
        
        Args:
            name: Tool name
            description: Tool description
        """
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tools.{name}")
    
    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool's main functionality.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Output data dictionary
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input data before execution.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    def handle_error(self, error: Exception) -> Dict[str, Any]:
        """
        Handle errors that occur during execution.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Error information dictionary
        """
        self.logger.error(f"Error in {self.name}: {str(error)}", exc_info=True)
        return {
            "success": False,
            "error": str(error),
            "tool": self.name,
        }
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point that validates input, executes, and handles errors.
        
        Args:
            input_data: Input data dictionary
            
        Returns:
            Output data dictionary
        """
        # Validate input
        is_valid, error_msg = self.validate_input(input_data)
        if not is_valid:
            self.logger.error(f"Input validation failed: {error_msg}")
            return {
                "success": False,
                "error": f"Input validation failed: {error_msg}",
                "tool": self.name,
            }
        
        # Execute
        try:
            self.logger.info(f"Executing {self.name}...")
            result = self.execute(input_data)
            self.logger.info(f"{self.name} completed successfully")
            return {
                "success": True,
                "tool": self.name,
                **result,
            }
        except Exception as e:
            return self.handle_error(e)
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"
