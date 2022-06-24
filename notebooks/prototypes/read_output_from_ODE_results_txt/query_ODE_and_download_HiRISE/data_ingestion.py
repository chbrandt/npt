"""
# ----------
# Listing:

bbox = {
    'latmin': -1,
    'latmax': 1,
    'lonmin': 179,
    'lonmax': 181
}

ode_results = find_intersect_products(boundingbox=bbox, dataset='mro/ctx/edr')
geojson = json2geojson(ode_results)

# ----------
# Download

path_archive_0 = '/mnt/das/mro/ctx/edr'

for product in geojson['FeaturesCollection']:
    out = download_product(product, path=path_archive_0)
    if out:
        product.update({'path_image': out})


# ----------
# Pre-Processing (Calibration / Map-projection)

## calibration
lvl2_list = []
for product in geojson['FeaturesCollection']:
    _lvl0 = product['path_image']
    _bname = _lvl0[:-4]
    _lvl1 = _bname + '.cub'
    _lvl2 = _bname + '.cal.cub'
    try:
        mroctx2isis(FROM=_lvl0, TO=_lvl1)
        spiceinit(FROM=_lvl1)
        ctxcal(FROM=_lvl1, TO=_lvl2)
        lvl2_list.append(_lvl2)
    except:
        continue

## map-project
map_defs = 'sinusoidal.map'
mosrange(FROMLIST=lvl2_list, TO=map_defs, projection='SINUSOIDAL', precision=0)
lvl3_list = []
for _lvl2 in lvl2_list:
    _lvl3 = _lvl2.replace('.cub','.map.cub')
    try:
        cam2map(FROM=_lvl2, TO=_lvl3, map=map_defs, pixres=map)
        lvl3_list.append(_lvl3)
    except:
        continue

# ----------
# Processing (Mosaic)

product = 'mosaic.cub'
automos(FROMLIST=lvl3_list, mosaic=product)

"""

def search(dataset_ID, bbox=None, product_IDs=None):
    """
    Search for products in dataset
    
    Search can access either (local) shapefiles or ODE's API
    """
    use_local_shapefiles = False
    if use_local_shapefiles:
        df = query_shapefile(dataset_ID, bbox, product_IDs)
    else:
        # use_ode_restapi
        df = query_ode(dataset_ID, bbox, product_IDs)
    return df


def find(product_IDs, output):
    


* Listing job/processing:
    - image_url = "query"
    - header_url = "query"
    - geometry = geometry
    - UTCStart = UTCStart
    - UTCEnd = UTCEnd
    - productId = PRODUCT_ID
    - datasetId = INSTRUMENT_HOST_ID + INSTRUMENT_ID + ODE_TYPE_ABBREVIATION
    - productType = TYPE

```
def script ( product_IDs, output ):
    def run (product_IDs):
        return [products_URLs]
    
    # Write geojson to 'output'
    return True/False
```

* Download:
    - image_path = "download"
    - header_path = "download"
```
def script ( feature, path, output ):
    def run (feature, path)
        assert image_url != "" and header_url
        # merge path + filename
        # download to absolute-path
        return absolute-path or None
    filename = run(feature, path)
    return # update feature
```