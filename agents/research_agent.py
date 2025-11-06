"""
Research Analyst Agent - Phase 1A
Analyzes trends and visual styles on social media.
"""
from typing import Dict, Any
import logging
from tools import TavilySearchTool

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Agent responsible for researching trends and visual styles.
    Uses Tavily API to find trending content on social media.
    """
    
    def __init__(self):
        self.name = "Research Analyst"
        self.search_tool = TavilySearchTool()
        self.logger = logging.getLogger(f"agents.{self.name}")
    
    def analyze_trends(self, topic: str, brand_hub: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze trends for the given topic on social media.
        
        Args:
            topic: The topic/theme to research
            brand_hub: Brand identity information
            
        Returns:
            Research insights including trending visuals, themes, and hashtags
        """
        self.logger.info(f"Analyzing trends for topic: {topic}")
        
        # Search for Instagram trends
        instagram_query = f"{topic} instagram reels trending visual style cinematography 2024"
        instagram_results = self.search_tool.run({"query": instagram_query})
        
        # Search for TikTok trends
        tiktok_query = f"{topic} tiktok trending video style aesthetics 2024"
        tiktok_results = self.search_tool.run({"query": tiktok_query})
        
        # Search for visual references
        visual_query = f"{topic} professional photography cinematography lighting composition"
        visual_results = self.search_tool.run({"query": visual_query})
        
        # Compile insights
        insights = {
            "topic": topic,
            "instagram_trends": self._extract_insights(instagram_results),
            "tiktok_trends": self._extract_insights(tiktok_results),
            "visual_references": self._extract_visual_refs(visual_results),
            "brand_alignment": self._check_brand_alignment(brand_hub),
        }
        
        self.logger.info("Trend analysis complete")
        return insights
    
    def _extract_insights(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key insights from search results."""
        if not search_results.get("success"):
            return {"error": "Search failed"}
        
        data = search_results
        return {
            "summary": data.get("answer", ""),
            "top_results": [
                {
                    "title": r.get("title", ""),
                    "key_points": r.get("content", "")[:200],
                }
                for r in data.get("results", [])[:3]
            ],
            "visual_examples": data.get("images", [])[:3],
        }
    
    def _extract_visual_refs(self, search_results: Dict[str, Any]) -> list:
        """Extract visual reference URLs."""
        if not search_results.get("success"):
            return []
        
        return search_results.get("images", [])[:5]
    
    def _check_brand_alignment(self, brand_hub: Dict[str, Any]) -> Dict[str, Any]:
        """Check how trends align with brand identity."""
        tone = brand_hub.get("tone_of_voice", "professional")
        colors = brand_hub.get("colors", [])
        
        return {
            "tone_of_voice": tone,
            "brand_colors": colors,
            "recommendations": f"Ensure visual style matches {tone} tone and incorporates brand colors: {', '.join(colors)}"
        }
    
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the agent.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with research insights
        """
        topic = state.get("topic", "")
        brand_hub = state.get("brand_hub", {})
        
        insights = self.analyze_trends(topic, brand_hub)
        
        return {
            **state,
            "research_insights": insights,
        }


if __name__ == "__main__":
    # Test the agent
    agent = ResearchAgent()
    
    test_state = {
        "topic": "morning coffee ritual",
        "brand_hub": {
            "tone_of_voice": "warm and inviting",
            "colors": ["#8B4513", "#F5DEB3", "#FFFFFF"],
        }
    }
    
    result = agent.run(test_state)
    print(result)
