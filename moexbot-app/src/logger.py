"""
Модуль логирования для MOEXbot.
"""
import logging
from pathlib import Path

__version__ = "1.0.0"


def setup_logger(log_file: str = "logs/moexbot.log") -> logging.Logger:
    """
    Настраивает логгер с цветным выводом в консоль и записью в файл.

    Args:
        log_file: Путь к файлу логов.

    Returns:
        Настроенный экземпляр Logger.
    """
    logger = logging.getLogger("MOEXbot")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
