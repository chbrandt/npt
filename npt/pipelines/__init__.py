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

    if gdf is None:
        log.info('Search returned no results.')
        return None

    if output_geojson:
        gdf.to_file(output_geojson, driver='GeoJSON', index=False)
        return output_geojson
    else:
        return gdf


def download(feature, basepath, progressbar=False):
    """
    Download data products and return updated feature (with 'image_path'/'label_path' added)

    Input:
    * feature:
        GeoJSON feature (from ODE search)
        Property 'image_url' is expected, field 'image_path' will be added
        Property 'label_url' is optional, field 'label_path' will be added
    * basepath:
        Base filesystem path (directory) where product will be downloaded
    * progressbar (False):
        If a (tqdm) progress-bar should show download progress
    """
    from npt.download import from_feature

    new_feature = from_feature(feature, basepath, progressbar=progressbar)

    return new_feature


def reduce(feature, basepath, tmpdir=None, keep_tmpdir=True, overwrite=False):
    """
    Reduce image to "science-ready" level, return updated feature

    Note: property 'tiff_path' is added to (new) feature

    Input:
    * feature:
        GeoJSON feature, with 'image_path' property
    * basepath:
        Base filesystem path (directory) where product will be downloaded
    * tmpdir:
        Temp directory where to do the processing/intermediate steps
    * keep_tmpdir:
        When and error occurs, to keep (True) or not to keep (False) temp data
    * overwrite:
        If False and output (file) already exists, skip processing
    """
    from npt.reduce import from_feature

    projection="sinusoidal"

    props = feature['properties']
    dataset = '/'.join(['mars', props['mission'], props['inst'], props['type']]).lower()

    new_feature = from_feature(feature, dataset, basepath=basepath, projection=projection,
                                tmpdir=tmpdir, keep_tmpdir=keep_tmpdir, overwrite=overwrite)

    return new_feature


def mosaic(geojson, basepath:str, output_geojson=None, method='warp', scale_factor=0.1):
    """
    Create Mosaic from images in 'geojson' input, return geojson with one mosaic/feature
    """
    from npt.mosaic import mosaic

    gdf = mosaic(geojson, basepath=basepath, method=method, scale_factor=scale_factor)

    if gdf is None:
        log.info('Mosaic failed to create.')
        return None

    if output_geojson:
        gdf.to_file(output_geojson, driver='GeoJSON', index=False)
        return output_geojson
    else:
        return gdf
