"""
Concept Director Agent

Generates multiple viral video concepts based on topic, research data, and brand identity.
Acts as the creative brainstorming phase before detailed scriptwriting.
"""

import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI
import json

from config.brand_loader import BrandIdentity

logger = logging.getLogger(__name__)


class ConceptDirectorAgent:
    """
    Concept Director Agent - Creative Brainstorming
    
    Generates 3-5 viral video concepts with different creative approaches,
    evaluates viral potential, and recommends the best concept.
    """
    
    def __init__(self, model: str = "gpt-4.1-mini"):
        """
        Initialize Concept Director Agent.
        
        Args:
            model: OpenAI model to use for concept generation
        """
        self.name = "Concept Director"
        self.model = model
        self.client = OpenAI()
        logger.info(f"{self.name} initialized with model: {model}")
    
    def generate_concepts(
        self,
        topic: str,
        research_data: Dict[str, Any],
        brand_identity: Optional[BrandIdentity] = None,
        num_concepts: int = 3,
        language: str = "sk",
        video_style: str = "cinematic"
    ) -> Dict[str, Any]:
        """
        Generate multiple viral video concepts.
        
        Args:
            topic: Video topic/subject
            research_data: Research insights from Research Agent
            brand_identity: Brand identity guidelines (optional)
            num_concepts: Number of concepts to generate (default: 3)
            language: Target language code
        
        Returns:
            Dictionary with:
                - concepts: List of concept dictionaries
                - recommended: Index of recommended concept
                - reasoning: Why this concept was recommended
        """
        logger.info(f"Generating {num_concepts} viral concepts for topic: {topic}")
        
        # Build the prompt
        prompt = self._build_concept_prompt(
            topic=topic,
            research_data=research_data,
            brand_identity=brand_identity,
            num_concepts=num_concepts,
            language=language,
            video_style=video_style
        )
        
        # Generate concepts using GPT-4
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,  # Higher creativity for concept generation
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            logger.info(f"Generated {len(result.get('concepts', []))} concepts")
            logger.info(f"Recommended concept: #{result.get('recommended', 1)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Concept generation failed: {e}")
            # Return fallback concept
            return self._fallback_concepts(topic, language)
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the Concept Director."""
        return """You are an expert Concept Director for viral social media video content.

Your role is to generate multiple creative concepts for short-form videos (30-60 seconds) that:
- Capture attention in the first 3 seconds
- Tell a compelling story or deliver value
- Are optimized for social media platforms (TikTok, Instagram Reels, YouTube Shorts)
- Align with brand identity and values
- Have high viral potential

For each concept, you evaluate:
- Hook strength (how attention-grabbing is the opening)
- Story arc (does it have a clear beginning, middle, end)
- Emotional impact (does it evoke feelings)
- Shareability (will people want to share it)
- Brand alignment (does it fit the brand identity)
- Production feasibility (can it be created with AI tools)

You think like a creative director who understands both artistry and virality.
You balance creativity with strategic thinking.
You always consider the target audience and platform algorithms.

IMPORTANT EXCLUSIONS:
- DO NOT generate ASMR concepts (requires specialized audio equipment and techniques)
- Focus on visual storytelling with voiceover narration
- Concepts must work with AI-generated visuals and voice

VIDEO STYLE AWARENESS:
You will be told which video style to optimize for. This is CRITICAL - concepts MUST match the style!

- PIKA style: 
  * REQUIRES a consistent main character/person throughout ALL scenes
  * Focus on character journey, transformation, or day-in-the-life
  * Examples: "Jana's morning coffee ritual", "A barista's day", "Coffee lover's journey"
  * ALL scenes must include the same person
  * NO pure product/object scenes without the character

- CINEMATIC style:
  * Focus on objects, nature, products, landscapes
  * NO consistent character needed (people optional, can be different)
  * Focus on visual beauty, motion, aesthetics
  * Examples: "The art of coffee", "From bean to cup", "Coffee craftsmanship"
  * Scenes can be pure product shots, nature, objects

- HYBRID style:
  * Mix of character scenes AND product scenes
  * Character scenes: Same person (like PIKA)
  * Product scenes: No character (like CINEMATIC)
  * Group scenes by subject (character group, product group, character group)
  * Examples: "Morning with coffee" (woman waking → coffee beans → woman drinking)

Adjust your concepts to STRICTLY match the specified style!"""
    
    def _build_concept_prompt(
        self,
        topic: str,
        research_data: Dict[str, Any],
        brand_identity: Optional[BrandIdentity],
        num_concepts: int,
        language: str,
        video_style: str
    ) -> str:
        """Build the concept generation prompt."""
        
        # Extract research insights
        trends = research_data.get("trends", [])
        viral_patterns = research_data.get("viral_patterns", [])
        
        # Format brand identity if provided
        brand_context = ""
        if brand_identity:
            brand_context = f"""
**BRAND IDENTITY TO FOLLOW:**
{brand_identity.get_context_string()}

**IMPORTANT:** All concepts MUST align with this brand identity. Consider:
- Visual style and mood
- Tone of voice and personality
- Brand values and messaging
- Content guidelines (must include/avoid)
"""
        
        prompt = f"""
Generate {num_concepts} creative viral video concepts for the following topic.

**TOPIC:** {topic}

**TARGET PLATFORM:** TikTok, Instagram Reels, YouTube Shorts (30-60 second videos)
**TARGET LANGUAGE:** {language}
**VIDEO STYLE:** {video_style.upper()}

**STYLE REQUIREMENTS (CRITICAL!):**
{self._get_style_requirements(video_style)}

**RESEARCH INSIGHTS:**
Current Trends: {', '.join(trends[:5]) if trends else 'No specific trends'}
Viral Patterns: {', '.join(viral_patterns[:5]) if viral_patterns else 'No specific patterns'}

{brand_context}

**YOUR TASK:**
Generate {num_concepts} DIFFERENT creative concepts. Each should have a unique approach:
- Concept 1: Educational + Entertaining
- Concept 2: Storytelling + Emotional
- Concept 3: ASMR/Satisfying + Visual
{f'- Concept 4: Tutorial + Value-driven' if num_concepts >= 4 else ''}
{f'- Concept 5: Behind-the-scenes + Authentic' if num_concepts >= 5 else ''}

For EACH concept, provide:
1. **Title:** Catchy concept name
2. **Hook:** The first 3-second attention grabber
3. **Story Arc:** Brief description of beginning, middle, end
4. **Style:** Visual and narrative style
5. **Viral Potential:** Score 1-10 with reasoning
6. **Brand Alignment:** How well it fits brand identity (if provided)
7. **Key Moments:** 3-4 key visual moments
8. **Emotional Journey:** What emotions it evokes

Then recommend the BEST concept and explain why.

Return JSON in this format:
{{
  "concepts": [
    {{
      "id": 1,
      "title": "Concept title",
      "hook": "First 3-second hook",
      "story_arc": "Beginning: ... Middle: ... End: ...",
      "style": "Visual and narrative style",
      "viral_potential": 8.5,
      "viral_reasoning": "Why this could go viral",
      "brand_alignment": "How it aligns with brand",
      "key_moments": ["Moment 1", "Moment 2", "Moment 3"],
      "emotional_journey": "Emotions evoked",
      "target_audience_appeal": "Why target audience will love it"
    }},
    ...
  ],
  "recommended": 2,
  "recommendation_reasoning": "Why concept #2 is the best choice"
}}
"""
        return prompt
    
    def _get_style_requirements(self, video_style: str) -> str:
        """Get style-specific requirements for concept generation."""
        
        if video_style == "pika":
            return """PIKA STYLE REQUIREMENTS:
- MUST feature a consistent main character/person in ALL scenes
- Focus on character journey, transformation, or day-in-the-life
- Examples: "Jana's morning ritual", "A day with a barista", "Coffee lover's journey"
- ALL scenes MUST include the same person doing different actions
- NO pure product/object scenes without the character
- Think: Character-driven storytelling
"""
        
        elif video_style == "cinematic":
            return """CINEMATIC STYLE REQUIREMENTS:
- Focus on objects, nature, products, landscapes, craftsmanship
- NO consistent character needed (people optional, can be different or none)
- Focus on visual beauty, motion, aesthetics, artistry
- Examples: "The art of coffee", "From bean to cup", "Coffee craftsmanship"
- Scenes can be pure product shots, nature close-ups, object details
- Think: Product-driven visual storytelling
"""
        
        elif video_style == "hybrid":
            return """HYBRID STYLE REQUIREMENTS:
- Mix of character scenes AND product scenes
- Character scenes: MUST feature the same person (like PIKA)
- Product scenes: NO character, focus on objects/nature (like CINEMATIC)
- Group scenes by subject (character group → product group → character group)
- Example: "Morning with coffee" (woman waking → coffee beans close-up → woman drinking)
- Think: Best of both worlds - character AND product storytelling
"""
        
        else:
            return f"Unknown style: {video_style}. Defaulting to CINEMATIC requirements."
    
    def _fallback_concepts(self, topic: str, language: str) -> Dict[str, Any]:
        """Generate fallback concepts if AI generation fails."""
        logger.info("Using fallback concept generation")
        
        return {
            "concepts": [
                {
                    "id": 1,
                    "title": f"The {topic} Story",
                    "hook": f"Watch this {topic} transformation",
                    "story_arc": "Beginning: Setup, Middle: Process, End: Result",
                    "style": "Cinematic storytelling",
                    "viral_potential": 7.0,
                    "viral_reasoning": "Transformation stories perform well",
                    "brand_alignment": "Neutral - works for most brands",
                    "key_moments": ["Opening shot", "Process detail", "Final reveal"],
                    "emotional_journey": "Curiosity → Engagement → Satisfaction",
                    "target_audience_appeal": "Universal appeal"
                }
            ],
            "recommended": 1,
            "recommendation_reasoning": "Fallback concept - safe and effective approach"
        }


# Export
__all__ = ["ConceptDirectorAgent"]
