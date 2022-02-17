"""
Define commands and sub-commands line interface
"""
import click
from click import argument,option

from npt import log

from npt.search import ode

from npt import datasets
# from npt.search import bbox as search_bbox
# from npt.pipelines import Search
from npt.utils.formatters import json_2_geojson
from npt.utils.bbox import string_2_dict as bbox_string_2_dict

# from npt.pipelines import Download
# from npt.utils import geojson

# from npt.pipelines import Processing
# from npt.pipelines import Mosaic



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
@option('--contains/--intersects', default=False, help="Bounding-box intersects or contains products' footprint")
@option('--coordsref', default='C0', help="Central coordinate reference: 'C0' or 'C180'.")
def search(dataset:str, bbox:str, output_geojson:str, contains:bool, coordsref:str):
    """
    Query 'provider'/'dataset' for data products in/on 'bbox'

    \b
    Attributes:
    - dataset:
        Options are: ['mars/mro/ctx/edr', 'mars/mro/hirise/rdrv11'].
    - bbox:
        Format: '[min,max,west,east]'
        Eg: if coords-ref=='C180': "[-0.5,0.5,359.5,0.5]"
        Eg: if coords-ref=='C0'    "[-0.5,0.5,-0.5,0.5]"
    - output_geojson:
        Output GeoJSON filename
    - contains:
        If True, consider only fully contained footprints inside B-Box;
        If False, consider footprints intersecting the bounding-box.
    """
    assert len(output_geojson.strip())>0

    bbox = bbox.replace('[','').replace(']','')
    bounding_box = bbox_string_2_dict(bbox)
    log.debug(bounding_box)

    match = 'contain' if contains else 'intersect'

    products = ode(bbox=bounding_box, dataset=dataset, match=match, bbox_ref=coordsref)

    products.to_file(output_geojson, driver='GeoJSON', index=False)

    return output_geojson


@main.command()
@argument('geojson_file')
@argument('basepath')
@option('--output', metavar='<.geojson>', default='', help="GeoJSON filename with query results")
@option('--progress/--silent', default=True, help="Print download progress")
def download(geojson_file, basepath, output, progress):
    """
    Download features' image_url/label_url data products
    """
    features = geojson.read(geojson_file)
    products = []
    for feature in features:
        mod_feature = Download.run(feature, base_path=basepath, progressbar=progress)
        products.append(mod_feature)
    log.debug(products)
    if output:
        json_2_geojson(products, filename=output)
    else:
        import json
        click.echo(json.dumps(products, indent=2))


@main.command()
@argument('filename')
@argument('basepath')
@option('--output', metavar='<.geojson>', default='', help="GeoJSON filename with query results")
@option('--tmpdir', default=None, help="Temp dir to use during processing")
# def reduce(geojson, basepath, output, tmpdir):
def from_geojson(filename:str, dataset:str, basepath:str="./data/reduced/",
                 projection:str="sinusoidal",
                 tmpdir:str=None, keep_tmpdir:bool=False,
                 overwrite:bool=False):
    """
    WIP
    """
    features = geojson.read(geojson_file)
    if docker_isis:
        from npt import isis
        isis.set_docker(docker_isis)
    products = []
    for feature in features:
        mod_feature = Processing.run(feature, output_path=basepath, tmpdir=tmpdir)
        products.append(mod_feature)
    log.debug(products)
    if output:
        json_2_geojson(products, filename=output)
    else:
        import json
        click.echo(json.dumps(products, indent=2))


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
