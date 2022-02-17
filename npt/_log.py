import logging
# fmt="%(levelname)s:%(funcName)s():%(lineno)i: %(message)s"
fmt="%(levelname)s:%(module)s.%(funcName)s(): %(message)s"
logging.basicConfig(level=logging.INFO, format=fmt)
log = logging.getLogger('npt')
log.setLevel('INFO')
