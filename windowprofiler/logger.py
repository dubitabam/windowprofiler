import sys
import logging
# pylint: disable=import-error
from config import Config
# pylint: enable=import-error


class Logger:

    __LOGGER = logging.getLogger("windowprofiler")


    @staticmethod
    def configure(
        config: Config,
    ):
        Logger.__LOGGER.setLevel(logging.getLevelName(config.log_level))

        formatter = logging.Formatter(
            fmt="[%(asctime)s][%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        if config.log_file:
            file_handler = logging.FileHandler(config.log_file)
            file_handler.setFormatter(formatter)
            Logger.__LOGGER.addHandler(file_handler)

        if config.log_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            Logger.__LOGGER.addHandler(console_handler)


    @staticmethod
    def debug(msg: str):
        Logger.__LOGGER.debug(msg)

    @staticmethod
    def info(msg: str):
        Logger.__LOGGER.info(msg)

    @staticmethod
    def warn(msg: str):
        Logger.__LOGGER.warn(msg)

    @staticmethod
    def error(msg: str):
        Logger.__LOGGER.error(msg)

    @staticmethod
    def critical(msg: str):
        Logger.__LOGGER.critical(msg)
