"""
Creative Strategist & Prompt Architect Agent - Phase 1B
Creates VIRAL-STYLE scenarios and prompts for professional social media videos.
Based on the workflow from successful AI content creators.
UPDATED: Now supports dual prompts for transition scenes (PikaMorph feature)
"""
from typing import Dict, Any, List, Optional
import logging
import json
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL
from config.brand_loader import BrandIdentity

logger = logging.getLogger(__name__)


class CreativeStrategistAgent:
    """
    Agent responsible for creating viral-style creative strategy and detailed prompts.
    Uses GPT-4 to generate punchy, fast-paced scenarios like professional content creators.
    """
    
    def __init__(self):
        self.name = "Creative Strategist & Prompt Architect"
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.logger = logging.getLogger(f"agents.{self.name}")
    
    def _get_language_name(self, code: str) -> str:
        """Convert language code to full name."""
        languages = {
            "sk": "Slovak",
            "cs": "Czech",
            "en": "English",
            "de": "German",
            "pl": "Polish",
            "hu": "Hungarian"
        }
        return languages.get(code, code.upper())
    
    def create_strategy(
        self,
        topic: str,
        brand_hub: Dict[str, Any],
        research_insights: Dict[str, Any],
        selected_concept: Optional[Dict[str, Any]] = None,
        brand_identity: Optional[BrandIdentity] = None,
        video_style: str = "cinematic",
        language: str = "sk"
    ) -> Dict[str, Any]:
        """
        Create comprehensive creative strategy and prompts for viral-style video.
        
        Args:
            topic: The topic/theme
            brand_hub: Brand identity
            research_insights: Research from Phase 1A
            
        Returns:
            Structured prompts for all 5 AI tools + voiceover
        """
        self.logger.info(f"Creating VIRAL-STYLE strategy for: {topic}")
        
        # Build context for GPT-4
        context = self._build_viral_context(topic, brand_hub, research_insights, selected_concept, brand_identity, video_style, language)
        
        # Generate prompts using GPT-4
        prompts = self._generate_viral_prompts(context)
        
        self.logger.info(f"Strategy created: {len(prompts.get('scenes', []))} scenes")
        return prompts
    
    def _build_viral_context(
        self,
        topic: str,
        brand_hub: Dict[str, Any],
        research_insights: Dict[str, Any],
        selected_concept: Optional[Dict[str, Any]] = None,
        brand_identity: Optional[BrandIdentity] = None,
        video_style: str = "cinematic",
        language: str = "sk"
    ) -> str:
        """Build context for viral-style content creation."""
        context = f"""
You are a PROFESSIONAL SOCIAL MEDIA CONTENT CREATOR who creates VIRAL videos.

Your style is inspired by successful creators who make fast-paced, engaging content that gets millions of views.

TOPIC: {topic}

BRAND IDENTITY:
{brand_identity.get_context_string() if brand_identity else f'''- Tone: {brand_hub.get('tone_of_voice', 'energetic, direct, authentic')}
- Colors: {', '.join(brand_hub.get('colors', ['modern', 'bold']))}
- Values: {brand_hub.get('values', 'authenticity, quality, innovation')}'''}

RESEARCH INSIGHTS:
{json.dumps(research_insights.get('instagram_trends', {}), indent=2)}

{f'''SELECTED CREATIVE CONCEPT:
Title: {selected_concept.get('title', '')}
Hook: {selected_concept.get('hook', '')}
Story Arc: {selected_concept.get('story_arc', '')}
Style: {selected_concept.get('style', '')}
Key Moments: {', '.join(selected_concept.get('key_moments', []))}

**IMPORTANT:** Build your detailed scenario based on this approved concept.
''' if selected_concept else ''}
===== YOUR MISSION =====

Create a 15-30 second VIRAL-STYLE vertical video (9:16) with:
- EXACTLY 8 FAST-PACED scenes (1.5-2.5 seconds each)
- PUNCHY, DIRECT voiceover (like the example below)
- CINEMATIC visuals that make people STOP SCROLLING

===== EXAMPLE VIRAL SCRIPT STYLE =====

"I spent six months testing AI tools. Here's what actually works. Midjourney? King for opening frames. Those cinematic shots that make people stop scrolling. This is your weapon. SeaDream 4 became my secret. Multiple shots that actually flow together. No more regenerating 50 times. Game changer."

Notice:
- SHORT sentences (3-7 words)
- DIRECT language ("Here's what works" not "I would like to share")
- POWER WORDS ("King", "weapon", "secret", "game changer")
- NO FLUFF (every word has purpose)
- FAST PACING (new idea every 2-3 seconds)

===== VOICEOVER SCRIPT REQUIREMENTS =====

**LANGUAGE:** Generate voiceover text in {self._get_language_name(language)} language.
- Visual prompts: Keep in English (for better AI image/video generation)
- Voiceover segments: Write in {self._get_language_name(language)} (language code: {language})

STRUCTURE (Hook → Value → Proof → CTA):
1. HOOK (0-3s): Grab attention immediately
   - "I tested 47 brands..."
   - "This changed everything..."
   - "Nobody talks about this..."

2. VALUE (3-15s): Deliver insights fast
   - Short, punchy statements
   - One idea per sentence
   - Power words and emphasis

3. PROOF (15-25s): Show credibility
   - Specific numbers/results
   - "Game changer" moments
   - Why it matters

4. CTA (25-30s): Strong ending
   - Direct question or challenge
   - "Are you in?"
   - "Your call."

STYLE RULES:
✅ DO:
- Use fragments. Short. Punchy.
- Power words: "King", "Secret", "Weapon", "Game changer"
- Numbers: "47 brands", "6 months", "50 times"
- Direct address: "You", "Your"
- Rhetorical questions: "Why?", "How?"
- Emphasis: ALL CAPS for key words (sparingly)

❌ DON'T:
- Long sentences
- Corporate speak
- "We believe that..." / "It is important to..."
- Passive voice
- Filler words
- Explanations (just state facts)

===== VISUAL SCENE REQUIREMENTS =====

You need to create prompts for EXACTLY 8 scenes using these AI tools:

1. **Opening Frame** (Midjourney via Apiframe) ⭐ CRITICAL
   - Scene 1 MUST ALWAYS use Midjourney (tool: "midjourney")
   - This is your scroll-stopping weapon
   - Cinematic, hyper-realistic, dramatic lighting
   - Film grain, 9:16 aspect ratio
   - Sets the visual style for ALL subsequent scenes
   - Example: "Cinematic shot, 9:16, morning light streams through window, hyper-realistic, film grain, style of cozy indie film"

2. **Style-Consistent Scenes** (Seedream 4 or Flux) ⭐ MAJOR
   - Scenes 2-3 should reference Scene 1's style
   - Add instruction: "Continue from opening frame. Style must be identical."
   - Maintain same lighting, color grading, character (if applicable)
   - Different angles/actions but same cinematic feel
   - Example: "Continue the sequence from Scene 1. Same lighting and style. Close-up of [action]."

3. **Multiple Angles** (Flux)
   - 2-3 variations of key moment
   - Same scene, different perspectives
   - Adds dynamism
   - Example: "Low angle shot", "Dutch angle", "Close-up"

4. **Text Overlay** (Ideogram)
   - 1-2 text graphics
   - Key words from script
   - Bold, readable typography
   - Example: "Bold text: 'GAME CHANGER' on dark background"

5. **Final Polish** (Nano Banana)
   - Face fixes if needed
   - Background adjustments
   - Final enhancements

===== VIDEO STYLE: {video_style.upper()} =====

{self._get_style_specific_instructions(video_style)}

===== OUTPUT FORMAT =====

Generate a JSON structure with:

```json
{{
  "hook": "Opening line that grabs attention",
  "voiceover_script": "Full 15-30s script in viral style",
  "scenes": [
    {{
      "number": 1,
      "description": "Opening frame - scroll-stopping hook",
      "tool": "midjourney",  // Scene 1 MUST be Midjourney
      "prompt": "Cinematic shot, 9:16, [your scene], morning/dramatic light, hyper-realistic, film grain, cozy indie film style",
      "content_type": "object|human_action|product",
      "duration": 2.0,
      "voiceover_segment": "Hook line (3-7 words)",
      "is_opening_frame": true  // Mark as reference for subsequent scenes
    }},
    {{
      "number": 2,
      "description": "Second scene - continues style",
      "tool": "seedream4|flux",
      "prompt": "Continue from Scene 1. Same lighting and cinematic style. [your action/angle].",
      "content_type": "human_action|object|product",
      "duration": 1.5-2.5,
      "voiceover_segment": "Next punchy line",
      "references_scene": 1  // Indicates style continuity
    }},
    // ... EXACTLY 8 total scenes
  ],
  "text_overlays": [
    {{
      "text": "GAME CHANGER",
      "timing": "at 15s"
    }}
  ]
}}
```

**IMPORTANT:** For each scene, set `content_type` correctly:
- "human_action" - person's face/body is the MAIN subject (full body action, gestures)
- "human_portrait" - face close-up, person standing/sitting (face is focus)
- "object" - inanimate objects OR hands/arms interacting with objects (e.g., pouring, holding)
- "product" - product showcase, unboxing, demonstration
- "text" - text overlay scene
- "transition" - smooth morph between two different states/objects/scenes
- "abstract" - artistic/abstract visuals

**RULES FOR CONTENT_TYPE:**
1. If you can't see the person's face clearly → use "object" not "human_action"
2. Hands/arms interacting with objects (pouring, holding, picking) → use "object"
3. Only use "human_action" if the person (face/body) is the MAIN FOCUS of the scene

**EXAMPLES:**
- "Handpicking coffee beans" → "object" (hands visible, but beans are focus)
- "Pouring water" → "object" (hands visible, but water/cup is focus)
- "Person drinking coffee" → "human_action" (person's face/expression is focus)
- "Close-up of face smiling" → "human_portrait" (face is main subject)

**NEW: TRANSITION SCENES (PikaMorph Feature)**

When you want to create a smooth morph between two different states, use `content_type: "transition"` and provide DUAL PROMPTS:

```json
{{
  "number": 3,
  "description": "Transition from grinding to brewing",
  "tool": "flux",
  "content_type": "transition",
  "prompts": {{
    "start": "Close-up of freshly ground coffee beans in grinder, dark roast, steam rising",
    "end": "Hot water flowing over coffee grounds in filter, golden brown, brewing process"
  }},
  "duration": 2.0,
  "voiceover_segment": "From beans to brew"
}}
```

**When to use transitions:**
- Between different actions (grinding → pouring)
- Between different states (cold → hot, solid → liquid)
- Between different objects that relate to the same theme
- To create dramatic visual flow between key moments

**Regular scenes still use single prompt:**
```json
{{
  "number": 1,
  "description": "Opening shot",
  "tool": "flux",
  "prompt": "Cinematic shot of coffee beans...",
  "content_type": "object",
  "duration": 2.0,
  "voiceover_segment": "Coffee. The morning ritual."
}}
```

===== CRITICAL RULES =====

1. **Pacing**: New visual every 1.5-2.5 seconds
2. **Script**: Punchy, direct, no fluff
3. **Visuals**: Cinematic, professional, consistent
4. **Structure**: Hook → Value → Proof → CTA
5. **Style**: Like a creator with millions of views
6. **Transitions**: Use dual prompts for smooth morphs between states
7. **SCENE-TO-SCENE CONSISTENCY**: Adjacent scenes should share similar style elements:
   - Maintain similar lighting mood (natural light → natural light, dramatic → dramatic)
   - Keep color temperature consistent (warm tones → warm tones, cool → cool)
   - Preserve camera style (cinematic → cinematic, product shot → product shot)
   - Example: "Scene 1: green leaves, natural light, soft focus" → "Scene 2: brown coffee beans, natural light, soft focus"
   - Allow natural transitions between subjects, but keep lighting/mood/style similar

Now create the strategy for: {topic}
"""
        return context
    
    def _get_style_specific_instructions(self, video_style: str) -> str:
        """Get style-specific instructions for CHARACTER, CINEMATIC, or HYBRID."""
        
        if video_style == "character":
            return """**CHARACTER STYLE REQUIREMENTS:**

You MUST generate a consistent character that appears throughout ALL scenes.

1. **Create Character Description:**
   Add a top-level field: "character_description": "Detailed description of the main character"
   Example: "Young woman, 25-30 years old, long brown hair, casual white sweater, warm smile, natural makeup"
   
2. **Scene 1 (Opening):**
   - Tool: "midjourney"
   - Include character in prompt: "Cinematic portrait, 9:16, {character_description}, {action}, morning light, hyper-realistic, film grain"
   - Mark as: "is_opening_frame": true
   
3. **Scene 2+ (Consistency):**
   - Tool: "seedream4" (uses Scene 1 as reference for same person)
   - Prompt MUST start with: "Same person from Scene 1. {character_description}. {new action/angle}."
   - Add: "references_scene": 1
   - Maintain exact same person, clothing, lighting style
   
4. **Transitions:**
   - ALL scenes use Pika morph transitions
   - Content type for character scenes: "human_action" or "human_portrait"

**CRITICAL:** Character description must be DETAILED and SPECIFIC (age, hair, clothing, features) so Seedream4 can maintain consistency."""
        
        elif video_style == "cinematic":
            return """**CINEMATIC STYLE REQUIREMENTS:**

Focus on beautiful motion and cinematography. NO consistent characters needed.

1. **Scene 1 (Opening):**
   - Tool: "midjourney"
   - Cinematic, dramatic, scroll-stopping
   
2. **Scene 2+ (Motion):**
   - Tool: "flux_dev" or "flux_pro" (NEVER seedream4)
   - Focus on objects, nature, products, abstract visuals
   - Content types: "object", "product", "abstract", "text"
   - **CRITICAL:** Use "object" for ALL scenes with hands/objects:
     * "Handpicking coffee beans" → "object"
     * "Pouring water" → "object"
     * "Holding cup" → "object"
   - AVOID "human_action" and "human_portrait" (inconsistent faces/people look bad)
   - Exception: Use "human_action" ONLY if person's face is clearly visible AND is main focus
   
3. **Transitions:**
   - Crossfade (300ms) between scenes
   - Smooth, professional

**BEST FOR:** Products, food, nature, abstract concepts, anything without people."""
        
        elif video_style == "hybrid":
            return """**HYBRID STYLE REQUIREMENTS:**

Smart mix of character scenes (Pika) and object scenes (Minimax).

1. **Character Scenes:**
   - If scene has consistent person: use "character_description" and "seedream4" with "references_scene": 1
   - Content type: "human_action" or "human_portrait"
   - Transition: Pika morph
   
2. **Object Scenes:**
   - No character needed
   - Tool: "flux_dev"
   - Content type: "object", "product", "abstract"
   - Transition: Crossfade
   
3. **Character Description (if any character scenes):**
   - Add "character_description" field if at least one scene has a person
   - Only apply to scenes with content_type "human_action" or "human_portrait"

**BEST FOR:** Mixed content (person + product), reviews, demonstrations."""
        
        else:
            return ""  # Default: no special instructions
    
    def _generate_viral_prompts(self, context: str) -> Dict[str, Any]:
        """Generate viral-style prompts using GPT-4."""
        
        system_prompt = """You are an expert viral content creator and prompt engineer.
You create fast-paced, engaging scripts and cinematic visual prompts.
Your content gets millions of views because it's PUNCHY, DIRECT, and VALUABLE.

Output ONLY valid JSON matching the exact structure provided in the context.
Make every word count. No fluff. Pure value.

IMPORTANT: For transition scenes, use the dual-prompt format with "prompts": {"start": "...", "end": "..."} instead of single "prompt" field.

ELEVENLABS EMOTION TAGS:
Enhance voiceover_script and voiceover_segment with inline emotion tags for dramatic delivery:
- [excited] for exciting moments
- [whispers] for secrets or intimate moments  
- [laughs] or [giggles] for humor
- [sighs] for disappointment or relief
- [thoughtful] for explanations
- [curious] for questions
- [sarcastic] for irony
- [happy], [sad], [angry], [nervous], [calm] for emotional states

Example: "Predstavte si [excited] úžasnú rannú kávu! [whispers] Tajomstvo je v čerstvých zrnkách... [giggles] Nie je to tak?"

Use tags strategically to make voiceover MORE ENGAGING and EMOTIONAL."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                temperature=0.9,  # Higher for more creative/punchy content
                max_tokens=2000,  # More tokens for detailed scenes
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            
            # Extract JSON from markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            prompts = json.loads(content)
            
            # Enhance visual prompts with technical details
            for scene in prompts.get("scenes", []):
                # Check if this is a transition scene with dual prompts
                if scene.get("content_type") == "transition" and "prompts" in scene:
                    # Enhance both start and end prompts
                    scene["prompts"]["start"] = self._enhance_visual_prompt(
                        scene["prompts"]["start"],
                        scene.get("tool", "flux")
                    )
                    scene["prompts"]["end"] = self._enhance_visual_prompt(
                        scene["prompts"]["end"],
                        scene.get("tool", "flux")
                    )
                elif "prompt" in scene:
                    # Regular single-prompt scene
                    scene["prompt"] = self._enhance_visual_prompt(
                        scene["prompt"],
                        scene.get("tool", "flux")
                    )
            
            # Ensure we have exactly 8 scenes
            scene_count = len(prompts.get("scenes", []))
            if scene_count != 8:
                self.logger.warning(f"Generated {scene_count} scenes, expected exactly 8")
            
            return prompts
            
        except Exception as e:
            self.logger.error(f"Failed to generate prompts: {e}")
            # Return fallback viral-style prompts
            return self._get_viral_fallback_prompts()
    
    def _enhance_visual_prompt(self, base_prompt: str, tool: str) -> str:
        """Add tool-specific technical enhancements to visual prompts."""
        
        # Common enhancements for all tools
        common = "9:16 vertical format, professional quality, sharp focus, detailed"
        
        # Tool-specific enhancements
        tool_specific = {
            "midjourney": "cinematic lighting, 35mm film, shallow depth of field, professional color grading, dramatic composition, film grain",
            "seedream4": "character consistency, same subject, coherent style, matching lighting",
            "flux": "photorealistic, high detail, dynamic angle, professional photography",
            "ideogram": "bold typography, high contrast, readable text, modern design, clean composition"
        }
        
        enhancement = tool_specific.get(tool, "cinematic, professional")
        
        return f"{base_prompt}. {common}, {enhancement}"
    
    def _get_viral_fallback_prompts(self) -> Dict[str, Any]:
        """Fallback viral-style prompts if GPT-4 fails."""
        return {
            "hook": "I tested this for 6 months. Here's what works.",
            "voiceover_script": "I tested this for 6 months. Here's what works. This tool? Game changer. Fast. Powerful. Easy. No BS. Just results. This is your weapon. The question is: are you in?",
            "scenes": [
                {
                    "number": 1,
                    "description": "Opening dramatic shot",
                    "tool": "flux",
                    "prompt": "Cinematic close-up, dramatic lighting",
                    "content_type": "object",
                    "duration": 2.0,
                    "voiceover_segment": "I tested this for 6 months."
                },
                {
                    "number": 2,
                    "description": "Key visual",
                    "tool": "flux",
                    "prompt": "Professional product shot",
                    "content_type": "product",
                    "duration": 2.0,
                    "voiceover_segment": "Here's what works."
                },
                {
                    "number": 3,
                    "description": "Transition to action",
                    "tool": "flux",
                    "content_type": "transition",
                    "prompts": {
                        "start": "Static product on table, professional lighting",
                        "end": "Product in use, dynamic action, motion blur"
                    },
                    "duration": 2.0,
                    "voiceover_segment": "This tool? Game changer."
                }
            ],
            "text_overlays": []
        }
