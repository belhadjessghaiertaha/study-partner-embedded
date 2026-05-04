"""
Study Partner Edge AI - Main Entry Point
Raspberry Pi 5 real-time cognitive sensor
"""
import sys
import argparse
from orchestrator import EdgeAIOrchestrator
from utils.logger import logger


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Study Partner Edge AI System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run indefinitely
  python main.py --duration 300     # Run for 5 minutes
  python main.py --config custom.json  # Use custom config
        """
    )
    
    parser.add_argument(
        '--config',
        default='config/config.json',
        help='Path to configuration file (default: config/config.json)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        help='Duration to run in seconds (default: infinite)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode (short duration, verbose logging)'
    )
    
    args = parser.parse_args()
    
    # Test mode
    if args.test:
        logger.info("Running in TEST mode (60 seconds)")
        args.duration = 60
    
    try:
        # Initialize orchestrator
        orchestrator = EdgeAIOrchestrator(config_path=args.config)
        
        # Run
        orchestrator.run(duration=args.duration)
        
        # Print final stats
        logger.info("=" * 60)
        logger.info("Final Statistics:")
        stats = orchestrator.get_stats()
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        logger.info("=" * 60)
        
        logger.info("Study Partner Edge AI shutdown successfully")
        return 0
    
    except KeyboardInterrupt:
        logger.info("\nShutdown by user")
        return 0
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
