# NEANIAS Planets Tools

This Python library provides the data/metadata processing tools running in
NEANIAS/MEEO backend planetary data store. We are handling data provided
by NASA/USGS Planetary Data System (PDS).

Main tools:

- `search`: query PDS' Orbital Data Explorer (ODE) using a bounding-box or a Product-ID.
- `download`: download data and metadata files from `search`
- `reduce`: process data from ODE to our data storing level (science-ready, GeoTIFF)
- `mosaic`: provide different functions for spatial mosaic'ing (GDAL, Rasterio, xarray)

General tools:

- `isis`: ISIS utilities, primarily used during `reduce` PDS files
- `utils`: misc utilities (data I/O, formatting, temp files support, etc.)
- `pipelines`: ADAM-DPS specific interface


## Install

You can a package URL with `pip`, the latest NPT release for instance.
Installing version 0.6.3:

```bash
$ pip install https://github.com/chbrandt/npt/archive/refs/tags/v0.6.3.tar.gz
```

## Python

- What's for datasets?:

```python
> import npt
> help(npt.datasets)

Help on package npt.datasets in npt:

NAME
    npt.datasets - Datasets dynamic import

PACKAGE CONTENTS


FUNCTIONS
    descriptors(dataset_id)
        Return descriptors set for given 'dataset'

    filters(dataset_id)
        Return filters set for given 'dataset'

    list()
        Return (sorted) list of available datasets

FILE
    /home/chbrandt/lib/npt/npt/datasets/__init__.py

>
```

- List the available datasets:

```python
> npt.datasets.list()

['mars/mex/hrsc/rdrv3',
 'mars/mex/hrsc/refdr3',
 'mars/mro/ctx/edr',
 'mars/mro/hirise/rdrv11']
>
```


- How to search for data products for a given dataset:

```python
> import npt
> help(npt.search)

Help on package npt.search in npt:

NAME
    npt.search - Query USGS/ODE API for image data products

PACKAGE CONTENTS
    _ode

FUNCTIONS
    ode(dataset: str, bbox: dict, match: str = 'intersect', bbox_ref: str = 'C0')
        Return GeoDataFrame with found data products as features

        Input:
        - dataset: name of the dataset (see `npt.datasets`)
        - bbox: bounding-box to query overlapping products.
                Dictionary keys: minlat, maxlat, westlon, eastlon;
                Latitude/longitude values range: (-90:90, -180:180)
        - match: how to consider overlapping matching footprints.
                 Options are: 'intersect', 'contain'
        - bbox_ref: if 'C0' (default), 'bbox' longitudes are centered at 0 (-180:180),
                    if 'C180', 'bbox' longitudes are centered at 180 (0:360).

DATA
    log = <Logger npt (INFO)>

FILE
    /home/chbrandt/lib/npt/npt/search/__init__.py

>
```

- Search HiRISE, for example:

```python
> # Define the dataset and region to query for images
> dataset = 'mars/mro/hirise/rdrv11'
> bbox = dict(
    westlon = -1,
    eastlon = 1,
    minlat = -1,
    maxlat = 1
  )
> # Search ODE
> gdf = npt.search.ode(dataset, bbox)
INFO:_ode.parse(): 11 products found
>
> # Print search results
> gdf
id mission    inst  ... image_kbytes                                          label_url                                         browse_url
0   PSP_007361_1800_RED     MRO  HIRISE  ...       454599  https://hirise.lpl.arizona.edu/PDS/RDR/PSP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
1   ESP_023672_1805_RED     MRO  HIRISE  ...       519022  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
2   ESP_023817_1800_RED     MRO  HIRISE  ...       219534  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
3   ESP_026507_1815_RED     MRO  HIRISE  ...       750494  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
4   ESP_029962_1800_RED     MRO  HIRISE  ...       193796  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
5   ESP_030463_1800_RED     MRO  HIRISE  ...       799775  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
6   ESP_039562_1800_RED     MRO  HIRISE  ...      1400359  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
7   ESP_041909_1800_RED     MRO  HIRISE  ...       290510  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
8   ESP_042542_1790_RED     MRO  HIRISE  ...       420884  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
9   ESP_044876_1800_RED     MRO  HIRISE  ...       390014  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
10  ESP_055359_1800_RED     MRO  HIRISE  ...       319407  https://hirise.lpl.arizona.edu/PDS/RDR/ESP/ORB...  https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
>
> # Print out first record
> gdf.iloc[0]
id                                                         PSP_007361_1800_RED
mission                                                                    MRO
inst                                                                    HIRISE
type                                                                    RDRV11
Target_name                                                               MARS
Footprints_cross_meridian                                                 True
Map_scale                                                                  0.5
Center_latitude                                                        -0.0145
Center_longitude                                                        0.0069
Easternmost_longitude                                                  359.989
Westernmost_longitude                                                   0.0249
Minimum_latitude                                                       -0.2453
Maximum_latitude                                                        0.2164
Emission_angle                                                        0.172712
Incidence_angle                                                      44.124317
Phase_angle                                                          43.953009
Solar_longitude                                                       34.80857
Observation_time                                       2008-02-21T00:58:55.081
Product_creation_time                                  2010-04-07T02:11:12.000
UTC_start_time                                         2008-02-21T00:58:50.835
UTC_stop_time                                          2008-02-21T00:58:59.328
geometry                     POLYGON ((0.0797 -0.2343, -0.011 -0.2453, -0.0...
image_url                    https://hirise.lpl.arizona.edu/PDS/RDR/PSP/ORB...
image_kbytes                                                            454599
label_url                    https://hirise.lpl.arizona.edu/PDS/RDR/PSP/ORB...
browse_url                   https://hirise.lpl.arizona.edu/PDS/EXTRAS/RDR/...
Name: 0, dtype: object

>
```

## Developers

To install NPT in _devel_ mode:

```bash
$ git clone https://github.com/chbrandt/npt.git
$ cd npt
$ pip install -e .
```


/.\
