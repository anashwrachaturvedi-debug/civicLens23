"""Structured application logging setup using Loguru.

Call :func:`configure_logging` once, during application startup, to
replace Python's default logging behavior with Loguru's structured,
rotated file and console logging across the whole app.
"""

import logging
import sys
from pathlib import Path

from loguru import logger

from app.core.config import settings


class InterceptHandler(logging.Handler):
    """Routes standard-library logging records into Loguru.

    Third-party libraries (uvicorn, sqlalchemy, fastapi) log through the
    standard ``logging`` module. This handler re-emits those records
    through Loguru so every log line in the application shares the same
    format, level filtering, and sinks.
    """

    def emit(self, record: logging.LogRecord) -> None:
        level = (
            logger.level(record.levelname).name
            if record.levelname in logger._core.levels  # type: ignore[attr-defined]
            else record.levelno
        )
        logger.opt(depth=6, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging() -> None:
    """Configure Loguru sinks and intercept standard-library logging."""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    logger.remove()

    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> "
            "- <level>{message}</level>"
        ),
        backtrace=False,
        diagnose=settings.DEBUG,
    )

    logger.add(
        log_dir / "civiclens.log",
        level=settings.LOG_LEVEL,
        rotation="00:00",
        retention="30 days",
        compression="zip",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

    logger.add(
        log_dir / "errors.log",
        level="ERROR",
        rotation="00:00",
        retention="90 days",
        compression="zip",
        enqueue=True,
        backtrace=True,
        diagnose=False,
    )

    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "sqlalchemy.engine"):
        logging.getLogger(logger_name).handlers = [InterceptHandler()]
        logging.getLogger(logger_name).propagate = False

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    logger.info("Logging configured (level={})", settings.LOG_LEVEL)