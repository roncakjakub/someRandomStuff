"""
LangGraph Workflow Orchestration
Coordinates all agents in a sequential pipeline.
"""
from typing import TypedDict, Dict, Any, List, Optional
import logging
from langgraph.graph import StateGraph, END
from agents import (
    ResearchAgent,
    CreativeStrategistAgent,
    VisualProductionAgent,
    VoiceoverAgent,
    AssemblyAgent,
)
from agents.concept_director import ConceptDirectorAgent
from workflow_router_v2 import WorkflowRouterV2
from config import load_brand_identity, BrandIdentity

logger = logging.getLogger(__name__)


class WorkflowState(TypedDict, total=False):
    """
    State schema for the workflow.
    Tracks all data as it flows through the pipeline.
    """
    # Input
    topic: str
    brand_hub: Dict[str, Any]
    run_output_dir: str  # Run-specific output directory
    brand_identity: Optional[BrandIdentity]  # Brand identity object
    background_music_path: Optional[str]  # Path to background music file
    music_volume: float  # Background music volume (0.0-1.0)
    
    # Phase 1A: Research
    research_insights: Dict[str, Any]
    
    # Phase 1B: Concept Generation
    concepts: Dict[str, Any]
    selected_concept: Dict[str, Any]
    
    # Phase 1C: Creative Strategy
    prompts: Dict[str, Any]
    
    # Phase 2: Workflow Planning
    workflow_plan: Any  # WorkflowPlan from router
    scene_plans: List[Dict[str, Any]]
    
    # Phase 2: Visual Production
    opening_frame: str
    scene_images: List[str]
    all_images: List[str]
    text_overlay_image: Optional[str]
    total_images: int
    
    # Phase 4: Voiceover
    voiceover_audio: str
    voiceover_script: str
    voiceover_language: str
    
    # Phase 5: Final Assembly
    final_video: str
    video_metadata: Dict[str, Any]
    
    # Metadata
    current_phase: str
    errors: List[Dict[str, Any]]


class SocialVideoWorkflow:
    """
    Main workflow orchestrator using LangGraph.
    Coordinates all agents in a sequential pipeline.
    """
    
    def __init__(
        self, 
        visual_quality: str = "dev", 
        default_language: str = "sk", 
        run_output_dir: str = None, 
        brand_file: Optional[str] = None,
        background_music_path: Optional[str] = None,
        music_volume: float = 0.15
    ):
        """
        Initialize the workflow.
        
        Args:
            visual_quality: Quality for image generation ("schnell", "dev", "pro")
            default_language: Default language for voiceover
            run_output_dir: Run-specific output directory path
            brand_file: Optional brand identity file to load
            background_music_path: Optional path to background music file
            music_volume: Background music volume (0.0-1.0, default 0.15)
        """
        self.logger = logging.getLogger("workflow")
        self.run_output_dir = run_output_dir
        self.default_language = default_language
        self.background_music_path = background_music_path
        self.music_volume = music_volume
        
        # Load brand identity if provided
        self.brand_identity = load_brand_identity(brand_file) if brand_file else None
        if self.brand_identity:
            self.logger.info(f"Loaded brand identity: {self.brand_identity.name}")
        
        # Initialize agents
        self.research_agent = ResearchAgent()
        self.concept_director = ConceptDirectorAgent()
        self.creative_agent = CreativeStrategistAgent()
        self.workflow_router = WorkflowRouterV2()
        self.visual_agent = VisualProductionAgent(quality=visual_quality)
        self.voiceover_agent = VoiceoverAgent(default_language=default_language)
        self.assembly_agent = AssemblyAgent()
        
        # Build workflow graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        # Create state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (agents)
        workflow.add_node("research", self._research_node)
        workflow.add_node("concept_generation", self._concept_generation_node)
        workflow.add_node("creative_strategy", self._creative_strategy_node)
        workflow.add_node("workflow_planning", self._workflow_planning_node)
        workflow.add_node("visual_production", self._visual_production_node)
        workflow.add_node("voiceover", self._voiceover_node)
        workflow.add_node("assembly", self._assembly_node)
        
        # Define edges (flow)
        workflow.set_entry_point("research")
        workflow.add_edge("research", "concept_generation")
        workflow.add_edge("concept_generation", "creative_strategy")
        workflow.add_edge("creative_strategy", "workflow_planning")
        workflow.add_edge("workflow_planning", "visual_production")
        workflow.add_edge("visual_production", "voiceover")
        workflow.add_edge("voiceover", "assembly")
        workflow.add_edge("assembly", END)
        
        return workflow.compile()
    
    def _research_node(self, state: WorkflowState) -> WorkflowState:
        """Phase 1A: Research trends and insights."""
        self.logger.info("=" * 60)
        self.logger.info("PHASE 1A: Research & Analysis")
        self.logger.info("=" * 60)
        
        try:
            result = self.research_agent.run(state)
            result["current_phase"] = "research_complete"
            result["brand_identity"] = self.brand_identity
            return result
        except Exception as e:
            self.logger.error(f"Research phase failed: {e}")
            raise
    
    def _concept_generation_node(self, state: WorkflowState) -> WorkflowState:
        """Phase 1B: Generate viral concepts."""
        self.logger.info("=" * 60)
        self.logger.info("PHASE 1B: Concept Generation")
        self.logger.info("=" * 60)
        
        try:
            concepts = self.concept_director.generate_concepts(
                topic=state["topic"],
                research_data=state["research_insights"],
                brand_identity=self.brand_identity,
                num_concepts=3,
                language=self.default_language
            )
            
            # Select recommended concept
            recommended_idx = concepts["recommended"] - 1
            selected_concept = concepts["concepts"][recommended_idx]
            
            self.logger.info(f"Generated {len(concepts['concepts'])} concepts")
            self.logger.info(f"Selected: {selected_concept['title']}")
            
            state["concepts"] = concepts
            state["selected_concept"] = selected_concept
            state["current_phase"] = "concepts_complete"
            
            return state
            
        except Exception as e:
            self.logger.error(f"Concept generation failed: {e}")
            # Fallback: continue without concept
            state["selected_concept"] = None
            return state
    
    def _creative_strategy_node(self, state: WorkflowState) -> WorkflowState:
        """Phase 1C: Create creative strategy and prompts."""
        self.logger.info("=" * 60)
        self.logger.info("PHASE 1C: Creative Strategy & Prompt Architecture")
        self.logger.info("=" * 60)
        
        try:
            # Call creative agent with new parameters
            prompts = self.creative_agent.create_strategy(
                topic=state["topic"],
                brand_hub=state["brand_hub"],
                research_insights=state["research_insights"],
                selected_concept=state.get("selected_concept"),
                brand_identity=self.brand_identity
            )
            
            state["prompts"] = prompts
            state["current_phase"] = "strategy_complete"
            return state
        except Exception as e:
            self.logger.error(f"Creative strategy phase failed: {e}")
            raise
    
    def _workflow_planning_node(self, state: WorkflowState) -> WorkflowState:
        """Phase 2: Plan workflow and select tools per scene."""
        self.logger.info("=" * 60)
        self.logger.info("PHASE 2: Workflow Planning & Tool Selection")
        self.logger.info("=" * 60)
        
        try:
            # Get scenes from creative strategy
            scenes = state["prompts"].get("scenes", [])
            
            # Analyze and plan
            workflow_plan = self.workflow_router.analyze_request(
                topic=state["topic"],
                scenes=scenes,  # Send full scenes with content_type
                brand_identity=self.brand_identity,  # Send brand identity
                max_cost=None,  # TODO: Get from CLI args
                max_time=None,  # TODO: Get from CLI args
                quality_preset="standard"  # TODO: Get from CLI args
            )
            
            self.logger.info(f"Workflow plan created:")
            self.logger.info(f"  - Image tools: {', '.join(workflow_plan.image_tools)}")
            self.logger.info(f"  - Video tools: {', '.join(workflow_plan.video_tools)}")
            self.logger.info(f"  - Estimated cost: ${workflow_plan.estimated_cost:.2f}")
            self.logger.info(f"  - Estimated time: {workflow_plan.estimated_time}s")
            
            state["workflow_plan"] = workflow_plan
            state["scene_plans"] = workflow_plan.scene_plans
            state["current_phase"] = "planning_complete"
            
            return state
            
        except Exception as e:
            self.logger.error(f"Workflow planning failed: {e}")
            # Fallback: continue without plan
            state["workflow_plan"] = None
            state["scene_plans"] = []
            return state
    
    def _visual_production_node(self, state: WorkflowState) -> WorkflowState:
        """Phase 3: Generate all visual content."""
        self.logger.info("=" * 60)
        self.logger.info("PHASE 3: Visual Content Production")
        self.logger.info("=" * 60)
        
        try:
            result = self.visual_agent.run(state)
            result["current_phase"] = "visuals_complete"
            return result
        except Exception as e:
            self.logger.error(f"Visual production phase failed: {e}")
            raise
    
    def _voiceover_node(self, state: WorkflowState) -> WorkflowState:
        """Phase 4: Generate voiceover audio."""
        self.logger.info("=" * 60)
        self.logger.info("PHASE 4: Voiceover Generation")
        self.logger.info("=" * 60)
        
        try:
            result = self.voiceover_agent.run(state)
            result["current_phase"] = "voiceover_complete"
            return result
        except Exception as e:
            self.logger.error(f"Voiceover phase failed: {e}")
            raise
    
    def _assembly_node(self, state: WorkflowState) -> WorkflowState:
        """Phase 5: Assemble final video."""
        self.logger.info("=" * 60)
        self.logger.info("PHASE 5: Final Video Assembly")
        self.logger.info("=" * 60)
        
        try:
            result = self.assembly_agent.run(state)
            result["current_phase"] = "complete"
            return result
        except Exception as e:
            self.logger.error(f"Assembly phase failed: {e}")
            raise
    
    def run(
        self,
        topic: str,
        brand_hub: Dict[str, Any] = None
    ) -> WorkflowState:
        """
        Execute the complete workflow.
        
        Args:
            topic: The topic/theme for the video
            brand_hub: Brand identity configuration
            
        Returns:
            Final workflow state with video path
        """
        self.logger.info("🚀 Starting Social Video Agent Workflow")
        self.logger.info(f"Topic: {topic}")
        
        # Initialize state
        initial_state: WorkflowState = {
            "topic": topic,
            "brand_hub": brand_hub or self._get_default_brand_hub(),
            "run_output_dir": self.run_output_dir,
            "background_music_path": self.background_music_path,
            "music_volume": self.music_volume,
            "current_phase": "initialized",
            "errors": [],
        }
        
        # Run workflow
        try:
            final_state = self.graph.invoke(initial_state)
            
            self.logger.info("=" * 60)
            self.logger.info("✅ WORKFLOW COMPLETE!")
            self.logger.info("=" * 60)
            self.logger.info(f"Final video: {final_state.get('final_video')}")
            
            return final_state
            
        except Exception as e:
            self.logger.error(f"Workflow failed: {e}")
            raise
    
    def _get_default_brand_hub(self) -> Dict[str, Any]:
        """Get default brand hub configuration."""
        return {
            "tone_of_voice": "professional and engaging",
            "colors": ["#1a1a1a", "#ffffff", "#4a90e2"],
            "values": "quality, authenticity, innovation",
            "language": "sk",
        }


if __name__ == "__main__":
    # Test the workflow
    import json
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create workflow
    workflow = SocialVideoWorkflow(
        visual_quality="schnell",  # Use fast model for testing
        default_language="sk"
    )
    
    # Test brand hub
    brand_hub = {
        "tone_of_voice": "warm and inviting",
        "colors": ["#8B4513", "#F5DEB3", "#FFFFFF"],
        "values": "quality coffee, morning rituals, mindfulness",
        "language": "sk",
    }
    
    # Run workflow
    try:
        result = workflow.run(
            topic="morning coffee ritual",
            brand_hub=brand_hub
        )
        
        print("\n" + "=" * 60)
        print("FINAL RESULT:")
        print("=" * 60)
        print(f"Video: {result.get('final_video')}")
        print(f"Images: {result.get('total_images')}")
        print(f"Audio: {result.get('voiceover_audio')}")
        
    except Exception as e:
        print(f"Error: {e}")
