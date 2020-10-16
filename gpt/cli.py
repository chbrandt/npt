"""
Define commands and sub-commands line interface
"""
import click
from click import argument,option

from gpt.search import bbox as search_bbox
from gpt.utils.formatters import json_2_geojson
from gpt.utils.bbox import string_2_dict as bbox_string_2_dict

class FormatHelp(click.Group):
    def format_help_text(self, ctx, formatter):
        if self.help:
            formatter.write_paragraph()
            for line in self.help.split('\n'):
                formatter.write_text(line)

@click.group(cls=FormatHelp)
def main():
    pass


@main.command()
@argument('provider')
@argument('dataset')
@argument('bbox')
@option('--output', default='', help="GeoJSON filename with query results")
# @option('--provider', default='ode', help="Choose interface/provider to query")
def search(bbox, dataset, output, provider='ode'):
    """
    Query 'provider'/'dataset' for 'bbox'-intersecting data products

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
    dataset_id = dataset

    bbox = bbox.replace('[','').replace(']','')
    bounding_box = bbox_string_2_dict(bbox)

    products = search_bbox(bbox=bounding_box,
                           dataset=dataset_id,
                           provider=provider)
    if output:
        json_2_geojson(products, filename=output)
    else:
        import json
        click.echo(json.dumps(products, indent=2))


@main.command()
def download():
    pass

# Command ISIS {format,calibrate,project}


if __name__ == '__main__':
    main()
