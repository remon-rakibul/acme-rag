import logging
import sys
from typing import Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger("healthcare_rag")
logger.setLevel(logging.INFO)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"healthcare_rag.{name}")
    return logger

