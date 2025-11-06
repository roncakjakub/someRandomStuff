"""
Tavily Search Tool for trend research and analysis.
"""
from typing import Dict, Any, Optional, List
from tavily import TavilyClient
import sys
from pathlib import Path as PathLib

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(PathLib(__file__).parent.parent))
    from tools.base_tool import BaseTool, retry_on_error
    from config.settings import TAVILY_API_KEY, TAVILY_SEARCH_DEPTH, TAVILY_MAX_RESULTS
else:
    from .base_tool import BaseTool, retry_on_error
    from config.settings import TAVILY_API_KEY, TAVILY_SEARCH_DEPTH, TAVILY_MAX_RESULTS


class TavilySearchTool(BaseTool):
    """
    Tool for searching and analyzing trends using Tavily API.
    """
    
    def __init__(self):
        super().__init__(
            name="tavily_search",
            description="Search for trending visual styles and themes on social media"
        )
        self.client = TavilyClient(api_key=TAVILY_API_KEY)
    
    def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate that query is provided."""
        if "query" not in input_data:
            return False, "Missing required field: query"
        if not isinstance(input_data["query"], str):
            return False, "Query must be a string"
        if len(input_data["query"].strip()) == 0:
            return False, "Query cannot be empty"
        return True, None
    
    @retry_on_error(max_retries=3, delay=5)
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute search query using Tavily.
        
        Args:
            input_data: Must contain 'query' field
            
        Returns:
            Dictionary with search results
        """
        query = input_data["query"]
        search_depth = input_data.get("search_depth", TAVILY_SEARCH_DEPTH)
        max_results = input_data.get("max_results", TAVILY_MAX_RESULTS)
        
        self.logger.info(f"Searching for: {query}")
        
        # Perform search
        response = self.client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results,
            include_images=True,
            include_answer=True,
        )
        
        # Extract relevant information
        results = {
            "query": query,
            "answer": response.get("answer", ""),
            "results": [],
            "images": response.get("images", [])[:5],  # Top 5 images
        }
        
        # Process search results
        for item in response.get("results", []):
            results["results"].append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", ""),
                "score": item.get("score", 0),
            })
        
        self.logger.info(f"Found {len(results['results'])} results")
        
        return results
    
    def search_trends(self, topic: str, platform: str = "instagram") -> Dict[str, Any]:
        """
        Search for trending content on specific platform.
        
        Args:
            topic: The topic to search for
            platform: Social media platform (instagram, tiktok, etc.)
            
        Returns:
            Trend analysis results
        """
        query = f"{topic} trending {platform} visual style aesthetics 2024"
        return self.run({"query": query})
    
    def search_visual_references(self, description: str) -> Dict[str, Any]:
        """
        Search for visual references based on description.
        
        Args:
            description: Description of desired visual style
            
        Returns:
            Visual reference results
        """
        query = f"{description} photography cinematography visual style examples"
        return self.run({"query": query})


if __name__ == "__main__":
    # Test the tool
    tool = TavilySearchTool()
    result = tool.search_trends("morning coffee ritual", "instagram")
    print(result)
