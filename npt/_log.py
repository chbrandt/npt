import logging
# # fmt="%(levelname)s:%(funcName)s():%(lineno)i: %(message)s"
# fmt="%(levelname)s:%(module)s.%(funcName)s(): %(message)s"
# logging.basicConfig(level=logging.INFO, format=fmt)
# log = logging.getLogger('npt')
# log.setLevel('INFO')
# log.set_level = log.setLevel

from pathlib import Path
_lib_path = Path(__file__).parents[1]
_leng_path = len(_lib_path.as_posix())

def filter(record: logging.LogRecord):
    record.package = record.pathname[_leng_path+1:]
    return record


log = logging.getLogger('npt')
log.setLevel(logging.DEBUG)
log.set_level = log.setLevel

handler = logging.StreamHandler()

fmt="%(levelname)s: [%(name)s - %(package)s] %(funcName)s(): %(message)s"
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)

handler.addFilter(filter)
log.addHandler(handler)
