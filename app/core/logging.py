import csv
import os
import sys
import logging
from loguru import logger


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def write_log_to_csv(data: list):
    os.makedirs("system_logs", exist_ok=True)
    with open("system_logs/logs.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(
                [
                    "request_id",
                    "request_datetime",
                    "url",
                    "client_host",
                    "response_time",
                    "status_code",
                    "success",
                ]
            )

        writer.writerow(data)


def setup_logging():
    os.makedirs("system_logs", exist_ok=True)

    # Remove default handlers
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    # Add file handler
    logger.add(
        "system_logs/app.log",
        rotation="10 MB",
        retention="10 days",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )

    # Intercept everything that goes to standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
