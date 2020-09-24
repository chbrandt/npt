from ._sh import isissh

def mosaic(filename_mapcubs_list='mapcubs.list', filename_mosaic='mosaic.cub'):
    isissh.automos(FROMLIST=filename_mapcubs_list, MOSAIC=filename_mosaic)
