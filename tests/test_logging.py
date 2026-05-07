"""测试 app/core/logging.py"""

from app.core.logging import get_logger, setup_logging


class TestLogging:
    def test_setup_logging_does_not_raise(self):
        setup_logging()

    def test_get_logger_returns_bound_logger(self):
        logger = get_logger("test")
        assert logger is not None
        logger.info("test message")

    def test_get_logger_default_name(self):
        logger = get_logger()
        assert logger is not None
