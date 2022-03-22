"""
Module to interface MEEO pipelines manager
"""
from npt import log

def search(dataset, bbox, match='intersect', bbox_ref='C0', output_geojson=None):
    """
    Write GeoJSON with products the bounding-box intersects/contains

    Input:
        dataset: name of the dataset (see `npt.datasets`)
            Ex: 'mars/mro/ctx/edr', 'mars/mex/hrsc/refdr3', 'mars/mro/hirise/rdrv11'
        bbox: bounding-box to query overlapping products.
            Dictionary keys: minlat, maxlat, westlon, eastlon;
            Latitude/longitude values range: (-90:90, -180:180)
        match: how to consider overlapping matching footprints.
            Options are: 'intersect', 'contain'
        bbox_ref: which meridian to consider as world/coordinates center ('C0' or 'C180')
            If 'C0' (default), consider longitude range as [-180:180].
            Use 'C180' to consider (longitude) coordinates in the range [0:360].
        output_geojson: path/filename for the output GeoJSON file.
    """
    from npt.search import ode

    if not bbox:
        return None

    gdf = ode(dataset=dataset, bbox=bbox, match=match, bbox_ref=bbox_ref)

    if output_geojson:
        gdf.to_file(output_geojson, driver='GeoJSON', index=False)
        return output_geojson
    else:
        return gdf
