"""
Define commands and sub-commands line interface
"""
import click
from click import argument,option

from .search import bbox as search_bbox
from .utils.io import json_2_geojson
from .utils.formaters import bbox_string_2_dict


@click.group()
def main():
    pass


@main.command()
@argument('bbox')
@argument('dataset')
@option('--output', default='', help="GeoJSON filename with query results")
@option('--provider', default='ode', help="Choose interface/provider to query")
def search(bbox, dataset, output, provider='ode'):
    """
    Query ODE for intersecting footprints to bbox.

    BBOX format: '[min,max,west,east]' (positive east [0:360])

    Datasets identifiers. Options are 'mars/mro/ctx/edr', 'mars/mro/hirise/rdrv11'.
    """
    dataset_id = dataset

    bounding_box = bbox_string_2_dict(bbox)

    products = search_bbox(bbox=bounding_box,
                           dataset=dataset_id,
                           provider=provider)
    if output:
        json_2_geojson(products, filename=output)
    else:
        click.echo(products)


@main.command()
def download():
    pass

# Command ISIS {format,calibrate,project}


if __name__ == '__main__':
    main()
