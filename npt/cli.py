"""
Define commands and sub-commands line interface
"""
import sys

import click
from click import argument,option

from npt import log
from npt import datasets
from npt.search import ode
from npt.download import from_geojson as download_geojson
from npt.reduce import from_geojson as reduce_geojson

from npt.utils import geojson
from npt.utils.bbox import string_2_dict as bbox_string_2_dict
from npt.utils.formatters import json_2_geojson


# === MAIN
@click.group()
@option('--debug', is_flag=True, default=False, help="Output DEBUG-level messages")
def main(debug:bool):
    """
    Interface to npt pipelines
    """
    if debug:
        log.setLevel('DEBUG')
# ===


@main.command()
def datasets_list():
    """List the supported datasets"""
    for dset in datasets.list():
        print(dset)


@main.command()
@argument('dataset')
@argument('bbox')
@argument('output_geojson')
@option('--contains/--intersects', is_flag=True, default=False, help="Bounding-box intersects or contains products' footprint")
@option('--coordsref', default='C0', help="Central coordinate reference: 'C0'(default) or 'C180'.")
def search(dataset:str, bbox:str, output_geojson:str, contains:bool, coordsref:str):
    """
    Query 'provider'/'dataset' for data products in/on 'bbox'

    \b
    Attributes:
        dataset: See `npt datasets-list` for options
        bbox: bounding-box definition, '[minlat,maxlat,westlon,eastlon]'
            Eg: if coords-ref=='C180': "[-0.5,0.5,359.5,0.5]"
            Eg: if coords-ref=='C0'    "[-0.5,0.5,-0.5,0.5]"
        output_geojson: output GeoJSON filename
        contains: if True, consider only footprints inside 'bbox' (False: all intersecting)
    """
    assert len(output_geojson.strip())>0

    bbox = bbox.replace('[','').replace(']','')
    bounding_box = bbox_string_2_dict(bbox)
    log.debug(bounding_box)

    match = 'contain' if contains else 'intersect'

    products = ode(bbox=bounding_box, dataset=dataset, match=match, bbox_ref=coordsref)

    if products is None:
        print("No products found.", file=sys.stderr)
        return None
    else:
        products.to_file(output_geojson, driver='GeoJSON', index=False)
        return output_geojson


@main.command()
@argument('input_geojson')
@argument('dest_path')
@argument('output_geojson')
@option('--progress/--silent', is_flag=True, default=True, help="Print download progress")
def download(input_geojson:str, dest_path:str, output_geojson:str, progress:bool):
    """
    Download features' image_url/label_url data products
    """
    assert len(output_geojson.strip())>0

    input_gjson = geojson.read(input_geojson)
    log.debug(input_gjson)

    result_gjson = download_geojson(input_gjson, basepath=dest_path, progressbar=progress)
    log.debug(result_gjson)

    geojson.write(result_gjson, output_geojson)

    return output_geojson


@main.command()
@argument('input_geojson')
@argument('dataset')
@argument('dest_path')
@argument('output_geojson')
@option('--projection', default='sinusoidal', help="Projection to lay images.")
@option('--tmpdir', default='', help="Temp-dir to use. Empty/none means a random one will be used.")
@option('--keep-tmpdir', is_flag=True, default=False, help="Keep temp-dir (don't delete it) if things fail.")
@option('--overwrite', is_flag=True, default=False, help="Force overwriting of products.")
@option('--docker-isis', default='', help="Container name to use for processing.")
def reduce(input_geojson:str, dataset:str, dest_path:str, output_geojson:str,
                 projection:str,
                 tmpdir:str, keep_tmpdir:bool,
                 overwrite:bool,
                 docker_isis:str):
    """
    Reduce image data to analysis/publication-ready (GeoTiff)
    """
    assert len(output_geojson.strip())>0

    input_gjson = geojson.read(input_geojson)
    log.debug(input_gjson)

    if docker_isis:
        from npt import isis
        isis.set_docker(docker_isis)

    result_gjson = reduce_geojson(input_gjson, dataset=dataset,
                                  basepath=dest_path, tmpdir=tmpdir)
    log.debug(result_gjson)

    geojson.write(result_gjson, output_geojson)

    return output_geojson



@main.command()
@argument('geojson_file')
@argument('basepath')
@option('--output', metavar='<.geojson>', default='', help="GeoJSON filename with query results")
@option('--tmpdir', default=None, help="Temp dir to use during processing")
def mosaic(geojson_file, basepath, output, tmpdir):
    """
    Make mosaic from files in 'input_geojson' file. Write GeoJSON with mosaic feature.
    """
    return Mosaic.run(geojson_file, basepath, output, tmpdir)


if __name__ == '__main__':
    main()
