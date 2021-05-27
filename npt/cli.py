"""
Define commands and sub-commands line interface
"""
import click
from click import argument,option

from npt import log

# from npt.search import bbox as search_bbox
from npt.pipelines import Search
from npt.utils.formatters import json_2_geojson
from npt.utils.bbox import string_2_dict as bbox_string_2_dict

from npt.pipelines import Download
from npt.utils import geojson

from npt.pipelines import Processing
from npt.pipelines import Mosaic



# === MAIN
@click.group()
@option('--debug', is_flag=True, default=False, help="Output DEBUG-level messages")
def main(debug):
    """
    Interface to npt pipelines
    """
    if debug:
        log.setLevel('DEBUG')
# ===



@main.command()
@argument('provider')
@argument('dataset')
@argument('bbox')
@option('--output', default='', help="GeoJSON filename with query results")
@option('--contains/--intersects', default=False, help="Bounding-box intersects or contains products' footprint")
# @option('--provider', default='ode', help="Choose interface/provider to query")
def search(bbox, dataset, output, provider, contains):
    """
    Query 'provider'/'dataset' for data products in/on 'bbox'

    \b
    Attributes:
    - provider: 'ODE'
        Query ODE for intersecting footprints to bbox.
    - dataset: <string>
        Options are: ['mars/mro/ctx/edr', 'mars/mro/hirise/rdrv11'].
    - bbox: <string>
        Format: '[min,max,west,east]' (global positive east [0:360])
        Eg,
            "[-0.5,0.5,359.5,0.5]"

    """
    bbox = bbox.replace('[','').replace(']','')
    bounding_box = bbox_string_2_dict(bbox)
    # products = search_bbox(bbox=bounding_box,
    #                        dataset=dataset_id,
    #                        provider=provider,
    #                        contains=contains)
    if output:
        # json_2_geojson(products, filename=output)
        products = Search.run(bounding_box=bounding_box,
                           dataset_id=dataset,
                           # provider=provider,
                           geojson_filename=output,
                           contains=contains)
    else:
        import json
        products = Search.run(bounding_box=bounding_box,
                           dataset_id=dataset,
                           # provider=provider,
                           contains=contains)
        click.echo(json.dumps(products, indent=2))


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
@argument('geojson_file')
@argument('basepath')
@option('--output', metavar='<.geojson>', default='', help="GeoJSON filename with query results")
@option('--tmpdir', default=None, help="Temp dir to use during processing")
def process(geojson_file, basepath, output, tmpdir):
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
