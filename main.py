"""
Main entry point for Social Video Agent.
Command-line interface for running the workflow.
"""
import argparse
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from workflow import SocialVideoWorkflow
from config import validate_config, OUTPUT_DIR, LOGS_DIR, DATA_DIR
import re


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    log_level = logging.DEBUG if verbose else logging.INFO
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"workflow_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging to: {log_file}")


def load_brand_hub(filepath: str = None) -> Dict[str, Any]:
    """
    Load brand hub configuration from JSON file.
    
    Args:
        filepath: Path to brand_hub.json file
        
    Returns:
        Brand hub dictionary
    """
    if filepath and Path(filepath).exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # Return default brand hub
    return {
        "tone_of_voice": "professional and engaging",
        "colors": ["#1a1a1a", "#ffffff", "#4a90e2"],
        "values": "quality, authenticity, innovation",
        "language": "sk",
    }


def create_run_output_dir(topic: str) -> Path:
    """
    Create a run-specific output directory based on topic and timestamp.
    
    Args:
        topic: The video topic
        
    Returns:
        Path to the run-specific output directory
    """
    # Create a clean folder name from topic
    # Remove special characters and limit length
    clean_topic = re.sub(r'[^a-zA-Z0-9\s-]', '', topic)
    clean_topic = re.sub(r'\s+', '_', clean_topic.strip())
    clean_topic = clean_topic[:30]  # Limit length
    
    # Add timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create folder name
    folder_name = f"{timestamp}_{clean_topic}"
    
    # Create directory
    run_dir = OUTPUT_DIR / folder_name
    run_dir.mkdir(parents=True, exist_ok=True)
    
    return run_dir


def save_results(state: Dict[str, Any], output_dir: Path) -> None:
    """
    Save workflow results to JSON file.
    
    Args:
        state: Final workflow state
        output_dir: Output directory
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f"results_{timestamp}.json"
    
    # Prepare results (remove non-serializable items)
    results = {
        "topic": state.get("topic"),
        "final_video": state.get("final_video"),
        "voiceover_audio": state.get("voiceover_audio"),
        "voiceover_script": state.get("voiceover_script"),
        "all_images": state.get("all_images", []),
        "video_metadata": state.get("video_metadata", {}),
        "prompts": state.get("prompts", {}),
        "timestamp": timestamp,
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Results saved to: {results_file}")


def print_banner():
    """Print application banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🎬 SOCIAL VIDEO AGENT 🎬                          ║
║                                                              ║
║     AI-Powered Multi-Agent Video Content Creation           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Social Video Agent - AI-powered video content creation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (fixed workflow, all tools)
  python main.py --topic "morning coffee ritual"
  
  # AI Router with budget preset (fast & cheap)
  python main.py --topic "morning coffee" --use-router --preset budget
  
  # AI Router with premium preset (max quality)
  python main.py --topic "product launch" --use-router --preset premium
  
  # AI Router with cost constraint
  python main.py --topic "quick tip" --use-router --max-cost 0.20
  
  # AI Router with time constraint (fast turnaround)
  python main.py --topic "breaking news" --use-router --max-time 120
  
  # High quality mode (fixed workflow)
  python main.py --topic "summer vibes" --quality pro --language en
  
  # Test mode
  python main.py --test
        """
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        help="Topic/theme for the video (e.g., 'morning coffee ritual')"
    )
    
    parser.add_argument(
        "--brand-hub",
        type=str,
        help="Path to brand_hub.json file (deprecated, use --brand-file)"
    )
    
    parser.add_argument(
        "--brand-file",
        type=str,
        help="Brand identity file to use (e.g., 'artisan_coffee' or path to JSON file)"
    )
    
    parser.add_argument(
        "--quality",
        type=str,
        choices=["schnell", "dev", "pro"],
        default="dev",
        help="Image generation quality: schnell (fast), dev (balanced), pro (best)"
    )
    
    parser.add_argument(
        "--language",
        type=str,
        default="sk",
        help="Voiceover language code (sk, cs, en, etc.)"
    )
    
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run with test data"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--use-router",
        action="store_true",
        help="Enable AI-Powered Workflow Router (intelligently selects tools)"
    )
    
    parser.add_argument(
        "--preset",
        type=str,
        choices=["budget", "standard", "premium", "viral"],
        help="Workflow preset: budget (fast/cheap), standard (balanced), premium (max quality), viral (optimized for viral potential)"
    )
    
    parser.add_argument(
        "--max-cost",
        type=float,
        help="Maximum budget in USD (only with --use-router)"
    )
    
    parser.add_argument(
        "--max-time",
        type=int,
        help="Maximum time in seconds (only with --use-router)"
    )
    
    parser.add_argument(
        "--background-music",
        type=str,
        help="Path to background music file (MP3, WAV, etc.)"
    )
    
    parser.add_argument(
        "--music-volume",
        type=float,
        default=0.15,
        help="Background music volume (0.0-1.0, default 0.15 = 15%%)"
    )
    
    parser.add_argument(
        "--style",
        type=str,
        choices=["character", "cinematic", "pika", "hybrid", "seedream", "kontext"],
        default="hybrid",
        help="Video style preset: character (consistent person), cinematic (beautiful motion), pika (smooth morph transitions), hybrid (smart mix), seedream (fast & cheap), kontext (environment consistency)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate configuration
    logger.info("Validating configuration...")
    is_valid, missing = validate_config()
    if not is_valid:
        logger.error("❌ Configuration validation failed!")
        logger.error("Missing environment variables:")
        for item in missing:
            logger.error(f"  - {item}")
        logger.error("\nPlease check your .env file and ensure all required API keys are set.")
        sys.exit(1)
    
    logger.info("✅ Configuration valid")
    
    # Get topic
    if args.test:
        topic = "morning coffee ritual"
        logger.info("🧪 Running in TEST mode")
    elif args.topic:
        topic = args.topic
    else:
        # Interactive mode
        print("\n" + "=" * 60)
        topic = input("Enter video topic/theme: ").strip()
        if not topic:
            logger.error("Topic cannot be empty")
            sys.exit(1)
    
    # Load brand hub
    brand_hub = load_brand_hub(args.brand_hub)
    brand_hub["language"] = args.language
    
    logger.info(f"Topic: {topic}")
    logger.info(f"Quality: {args.quality}")
    logger.info(f"Language: {args.language}")
    logger.info(f"Style: {args.style}")
    
    # AI Router integration
    workflow_plan = None
    # Router configuration (handled inside workflow)
    if args.use_router:
        logger.info("\n🤖 AI-Powered Router ENABLED")
        if args.preset:
            logger.info(f"Using preset: {args.preset}")
        if args.max_cost:
            logger.info(f"Max cost: ${args.max_cost}")
        if args.max_time:
            logger.info(f"Max time: {args.max_time}s")
        logger.info("  → Router will analyze scenes and select optimal tools inside workflow")
    else:
        logger.info("\n🔧 Router DISABLED - Using default tools")
        logger.info("  Tip: Use --use-router to enable intelligent tool selection")
    
    # Create run-specific output directory
    run_output_dir = create_run_output_dir(topic)
    logger.info(f"\nOutput directory: {run_output_dir}")
    
    # Create workflow
    logger.info("\nInitializing workflow...")
    
    # Initialize workflow
    workflow = SocialVideoWorkflow(
        visual_quality=args.quality,
        default_language=args.language,
        run_output_dir=run_output_dir,
        brand_file=args.brand_file,
        background_music_path=args.background_music,
        music_volume=args.music_volume,
        video_style=args.style
    )
    
    # Run workflow
    try:
        print("\n" + "=" * 60)
        print("🚀 STARTING VIDEO GENERATION WORKFLOW")
        print("=" * 60)
        
        final_state = workflow.run(
            topic=topic,
            brand_hub=brand_hub
        )
        
        # Print results
        print("\n" + "=" * 60)
        print("✅ VIDEO GENERATION COMPLETE!")
        print("=" * 60)
        print(f"\n📹 Final Video: {final_state.get('final_video')}")
        print(f"🎤 Voiceover: {final_state.get('voiceover_audio')}")
        print(f"🖼️  Images: {final_state.get('total_images')}")
        print(f"\n📂 All files saved to: {run_output_dir}")
        
        # Save results
        save_results(final_state, run_output_dir)
        
        print("\n✨ Done! Your video is ready.")
        
    except KeyboardInterrupt:
        logger.warning("\n\n⚠️  Workflow interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n\n❌ Workflow failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
