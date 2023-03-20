from warehouse_postalcode_generator.cli import cli
import logging
import sys

logger = logging.getLogger("warehouse_postalcode_generator")
logger.setLevel(logging.DEBUG)

logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

streamHandler = logging.StreamHandler(stream=sys.stdout)
streamHandler.setFormatter(logFormatter)
logger.addHandler(streamHandler)

fileHandler = logging.FileHandler(
    filename="warehouse_postalcode_generator.log", mode="w"
)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

cli()
