import logging, sys
from pythonjsonlogger import jsonlogger
def configure_logging(level="INFO"):
    h=logging.StreamHandler(sys.stdout)
    h.setFormatter(jsonlogger.JsonFormatter("%(levelname)s %(name)s %(message)s"))
    root=logging.getLogger(); root.setLevel(level); root.handlers=[h]