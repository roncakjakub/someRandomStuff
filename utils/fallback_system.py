"""
Fallback System for Tool Execution

This module implements a fallback system that automatically tries alternative tools
when the primary tool fails due to insufficient credits, content policy, or other errors.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from config.tool_metadata import get_fallback_tools, get_tool_metadata


class ToolExecutionError(Exception):
    """Base exception for tool execution errors."""
    pass


class InsufficientCreditsError(ToolExecutionError):
    """Raised when tool fails due to insufficient credits."""
    pass


class ContentPolicyError(ToolExecutionError):
    """Raised when tool fails due to content policy violation."""
    pass


class AllToolsFailedError(ToolExecutionError):
    """Raised when all tools in the fallback chain fail."""
    pass


class FallbackSystem:
    """
    System for executing tools with automatic fallback to alternatives.
    
    Usage:
        fallback = FallbackSystem()
        result = fallback.execute_with_fallback(
            primary_tool="veo31_flf2v",
            input_data={"first_frame_image": "...", "prompt": "..."}
        )
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.execution_log: List[Dict[str, Any]] = []
    
    def execute_with_fallback(
        self,
        primary_tool: str,
        input_data: Dict[str, Any],
        tool_executor: Callable[[str, Dict[str, Any]], Dict[str, Any]],
        max_attempts: int = 3
    ) -> Dict[str, Any]:
        """
        Execute a tool with automatic fallback to alternatives.
        
        Args:
            primary_tool: Name of the primary tool to try first
            input_data: Input data for the tool
            tool_executor: Function that executes a tool (tool_name, input_data) -> result
            max_attempts: Maximum number of tools to try (default: 3)
            
        Returns:
            Result dictionary from the successful tool
            
        Raises:
            AllToolsFailedError: If all tools in the fallback chain fail
        """
        # Build fallback chain
        fallback_chain = self._build_fallback_chain(primary_tool, max_attempts)
        
        self.logger.info(f"Executing with fallback chain: {' -> '.join(fallback_chain)}")
        
        # Try each tool in the chain
        for i, tool_name in enumerate(fallback_chain):
            try:
                self.logger.info(f"Attempting tool {i+1}/{len(fallback_chain)}: {tool_name}")
                
                # Execute the tool
                result = tool_executor(tool_name, input_data)
                
                # Log success
                self._log_execution(tool_name, "success", None)
                self.logger.info(f"✅ SUCCESS: {tool_name} completed successfully")
                
                # Add fallback info to result
                result["fallback_info"] = {
                    "primary_tool": primary_tool,
                    "executed_tool": tool_name,
                    "attempt_number": i + 1,
                    "fallback_used": (tool_name != primary_tool)
                }
                
                return result
                
            except InsufficientCreditsError as e:
                self._log_execution(tool_name, "failed", "insufficient_credits")
                self.logger.warning(f"❌ {tool_name} failed: Insufficient credits")
                self.logger.info(f"   Trying next fallback...")
                continue
                
            except ContentPolicyError as e:
                self._log_execution(tool_name, "failed", "content_policy")
                self.logger.warning(f"❌ {tool_name} failed: Content policy violation")
                self.logger.info(f"   Trying next fallback...")
                continue
                
            except Exception as e:
                self._log_execution(tool_name, "failed", f"error: {str(e)}")
                self.logger.warning(f"❌ {tool_name} failed: {str(e)}")
                self.logger.info(f"   Trying next fallback...")
                continue
        
        # All tools failed
        self.logger.error(f"❌ ALL TOOLS FAILED in fallback chain: {fallback_chain}")
        raise AllToolsFailedError(
            f"All tools failed in fallback chain: {fallback_chain}. "
            f"Check execution log for details."
        )
    
    def _build_fallback_chain(self, primary_tool: str, max_attempts: int) -> List[str]:
        """
        Build a fallback chain starting from the primary tool.
        
        Args:
            primary_tool: Name of the primary tool
            max_attempts: Maximum number of tools to include
            
        Returns:
            List of tool names in order of priority
        """
        chain = [primary_tool]
        
        # Get fallback tools from metadata
        fallback_tools = get_fallback_tools(primary_tool)
        
        # Add fallback tools up to max_attempts
        for tool in fallback_tools:
            if len(chain) >= max_attempts:
                break
            if tool not in chain:  # Avoid duplicates
                chain.append(tool)
        
        return chain
    
    def _log_execution(self, tool_name: str, status: str, error: Optional[str] = None):
        """Log tool execution attempt."""
        self.execution_log.append({
            "tool": tool_name,
            "status": status,
            "error": error
        })
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get the execution log."""
        return self.execution_log
    
    def clear_execution_log(self):
        """Clear the execution log."""
        self.execution_log = []


def execute_tool_with_fallback(
    primary_tool: str,
    input_data: Dict[str, Any],
    tool_executor: Callable[[str, Dict[str, Any]], Dict[str, Any]],
    max_attempts: int = 3
) -> Dict[str, Any]:
    """
    Convenience function for executing a tool with fallback.
    
    Args:
        primary_tool: Name of the primary tool to try first
        input_data: Input data for the tool
        tool_executor: Function that executes a tool (tool_name, input_data) -> result
        max_attempts: Maximum number of tools to try (default: 3)
        
    Returns:
        Result dictionary from the successful tool
        
    Raises:
        AllToolsFailedError: If all tools in the fallback chain fail
    
    Example:
        def my_tool_executor(tool_name, input_data):
            tool = get_tool_instance(tool_name)
            return tool.execute(input_data)
        
        result = execute_tool_with_fallback(
            primary_tool="veo31_flf2v",
            input_data={"first_frame_image": "...", "prompt": "..."},
            tool_executor=my_tool_executor
        )
    """
    fallback_system = FallbackSystem()
    return fallback_system.execute_with_fallback(
        primary_tool=primary_tool,
        input_data=input_data,
        tool_executor=tool_executor,
        max_attempts=max_attempts
    )


# Export
__all__ = [
    "FallbackSystem",
    "ToolExecutionError",
    "InsufficientCreditsError",
    "ContentPolicyError",
    "AllToolsFailedError",
    "execute_tool_with_fallback"
]
