"""
Define commands and sub-commands line interface
"""
import click
from click import argument,option

from .pipelines import Search


@click.group()
def main():
    pass

@main.command()
@argument('bbox')
@argument('dataset')
@option('--output', default='', help="GeoJSON filename with query results")
def search(bbox,dataset,output):
    """
    Query ODE for intersecting footprints to bbox.

    BBOX format: 'min,max,west,east' (positive east [0:360])

    Datasets identifiers. Options are 'mro/ctx/edr', 'mro/hirise/rdrv11'.
    """
    _lbl = ['minlat','maxlat','westlon','eastlon']
    _bbx = [float(c) for c in bbox.split(',')]
    bounding_box = {k:v for k,v in zip(_lbl,_bbx)} 
    dataset_id = dataset
    _search = Search()
    products = _search.query_footprints(bbox=bounding_box,
                                       dataset=dataset_id)
    if output:
        gdf = Search.write_geojson(products, filename=output)
    else:
        click.echo(products)


@main.command()
def download():
    pass

# Command ISIS {format,calibrate,project}



if __name__ == '__main__':
    main()
