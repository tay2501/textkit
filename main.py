"""
Main entry point for the Text Processing Toolkit.

This is the main entry point for the Polylith-based text processing system
with modular components and modern CLI interface.
"""

from textkit.cli_interface import run_cli


def main():
    """Main entry point for the application with enhanced logging."""
    try:
        # Initialize structured logging first
        from textkit.config_manager.settings import configure_logging
        configure_logging()
        
        # Get logger after configuration
        import structlog
        logger = structlog.get_logger(__name__)
        
        logger.info("application_starting", version="0.1.0")
        
        # Run the CLI application
        run_cli()
        
        logger.info("application_completed")
        
    except KeyboardInterrupt:
        logger = structlog.get_logger(__name__)
        logger.info("application_interrupted_by_user")
        raise
    except Exception as e:
        logger = structlog.get_logger(__name__)
        logger.exception(
            "application_failed_unexpectedly",
            error_type=type(e).__name__,
            error=str(e)
        )
        raise


if __name__ == "__main__":
    main()
