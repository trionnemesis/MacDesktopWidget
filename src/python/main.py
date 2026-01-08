"""
Main entry point for MacDesktopWidget application.
"""
import sys
import signal
import logging

from core.app import create_app

logger = logging.getLogger(__name__)


def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully."""
    logger.info("\nReceived interrupt signal, shutting down...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create application
        qt_app, app = create_app()
        
        # Start the application
        app.start()
        
        # Print startup message
        print("\n" + "="*60)
        print("  MacDesktopWidget - System Monitoring with AI")
        print("="*60)
        print("\n📊 Monitoring your system resources...")
        print("🤖 AI suggestions will appear when anomalies are detected\n")
        print("Press Ctrl+C to exit\n")
        
        # Run Qt event loop
        sys.exit(qt_app.exec())
    
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
