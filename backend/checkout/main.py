import uvicorn
import sys
import os

# Setup logging before importing other modules
from checkout.utils.logging_config import setup_logging, get_logger
from checkout.rest.api import app

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", None)  # Optional log file path
setup_logging(log_level=log_level, log_file=log_file)

logger = get_logger(__name__)


def main():
    """Main entry point for the checkout application"""
    logger.info("=" * 50)
    logger.info("Starting Restaurant Checkout API")
    logger.info("=" * 50)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Log level: {log_level}")
    if log_file:
        logger.info(f"Log file: {log_file}")

    try:
        logger.info("Starting uvicorn server on host=0.0.0.0, port=8000")
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level=log_level.lower())
    except KeyboardInterrupt:
        logger.info("Application shutdown requested by user")
    except Exception as e:
        logger.error(f"Application failed to start: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Restaurant Checkout API shutdown complete")


if __name__ == "__main__":
    main()
