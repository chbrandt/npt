API_URL = 'https://oderest.rsl.wustl.edu/live2'

DESCRIPTORS = {
    'ctx': {
        'product_image': ('Description','PRODUCT DATA FILE WITH LABEL'),
        'browse_image': ('Description','BROWSE IMAGE'),
        'browse_thumbnail': ('Description','THUMBNAIL IMAGE')
    },
    'hirise': {
        'product_image': ('Description', 'PRODUCT DATA FILE'),
        'product_label': ('Description', 'PRODUCT LABEL FILE'),
        'browse_image': ('Description', 'BROWSE'),
        'browse_thumbnail': ('Description', 'THUMBNAIL')
    }
}

DATASETS = {
    'ctx': {
        'ptype': 'edr',
        'instr': 'ctx',
        'host': 'mro'
    },
    'hirise': {
        'ptype': 'rdrv11',
        'instr': 'hirise',
        'host': 'mex'
    }
}


def request_product(PRODUCTID, api_endpoint):
    import requests
    payload = dict(
        query='product',
        results='fmp',
        output='JSON',
        productid=PRODUCTID
    )
    #payload.update({'pretty':True})
    return requests.get(api_endpoint, params=payload)


def request_products(api_endpoint, bbox, target=None, host=None, instr=None, ptype=None):
    """
    bbox = {
        'minlat': [-65:65],
        'minlat': [-65:65],
        'westlon': [0:360],
        'eastlon': [0:360]
    }
    'ptype' (eg, "rdrv11") is used only when 'instr' is also defined (e.g, "hirise").
    """
    import requests
    payload = dict(
        query='product',
        results='fmpc',
        output='JSON',
        loc='f',
        minlat=bbox['minlat'],
        maxlat=bbox['maxlat'],
        westlon=bbox['westlon'],
        eastlon=bbox['eastlon']
    )
    if target:
        payload.update({'target':target})
    if host:
        payload.update({'ihid':host})
    if instr:
        payload.update({'iid':instr})
        if ptype:
            payload.update({'pt':ptype})
    #payload.update({'pretty':True})
    return requests.get(api_endpoint, params=payload)


def requested_product_files(request):
    product_files = request.json()['ODEResults']['Products']['Product']['Product_files']['Product_file']
    return product_files


def readout_product_files(product_json):
    product_files = product_json['Product_files']['Product_file']
    return product_files


def readout_product_footprint(product_json):
    # 'Footprint_geometry' and 'Footprint_C0_geometry' may contain 'GEOMETRYCOLLECTION'
    # when the footprint cross the meridian in "c180" or "c0" frames
    #product_geom = request.json()['ODEResults']['Products']['Product']['Footprint_geometry']
    #product_geom = request.json()['ODEResults']['Products']['Product']['Footprint_C0_geometry']
    product_geom = product_json['Footprint_GL_geometry']
    return product_geom


#
#TODO: ler uma lista de produtos: foreach product in "['ODEResults']['Products']"
#


def readout_product_meta(product_json):
    product = {}
    # <pdsid>ESP_011712_1820_COLOR</pdsid>
    product['id'] = product_json['pdsid']
    # <ihid>MRO</ihid>
    product['mission'] = product_json['ihid']
    # <iid>HIRISE</iid>
    product['inst'] = product_json['iid']
    # <pt>RDRV11</pt>
    product['type'] = product_json['pt']
    return product

    
def requested_products(request):
    assert request.status_code == 200 and request.json()['ODEResults']['Status'].lower() == 'success'
    products = request.json()['ODEResults']['Products']['Product']
    assert isinstance(products, list), "Was expecting 'list', got '{}' instead".format(type(products))
    return products
    
    
def find_product_file(product_files, product_type, descriptors=DESCRIPTORS):
    _key,_val = descriptors[product_type]
    pfl = list(filter(lambda pf:pf[_key]==_val, product_files))
    _multiple_matches = "I was expecting only one Product matching ptype '{}' bu got '{}'."
    assert len(pfl) == 1, _multiple_matches.format(product_type, len(pfl))
    return pfl[0]

