import logging
import sys

LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | "
    "%(name)s | %(message)s"
)

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,           # SHOW INFO LOGS
        format=LOG_FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),  # TERMINAL
            logging.FileHandler("logs/app.log") # FILE
        ],
        force=True  # OVERRIDE uvicorn defaults
    )

    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
