import requests

from gpt import log
from gpt import query
from gpt import datasets

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


DB_ID = 'usgs_ode'

class ODE(query.Query):
    _result = None
    def __init__(self, target, mission, instrument, product_type):
        super().__init__()
        self.set_dataset(target, mission, instrument, product_type)

    def list_datasets(self):
        # return datasets.ode.list()
        _datasets = datasets.db.query("""
            SELECT * FROM datasets WHERE db_id == '{db_id}'
            """.format(db_id=DB_ID))

    def set_dataset(self, target, host, instr, ptype, dataset=None):
        """
        Args:
            target:
            host:
            instr:
            ptype:

        Returns:
            ODE
        """
        if dataset is None:
            msg = "Either set 'dataset' or all the others."
            assert all([target, host, instr, ptype]), msg
        self.host = host
        self.instr = instr
        self.ptype = ptype
        self.target = target
        return self

    def query_bbox(self, bbox, contains=False):
        """
        Return list of found products (in dictionaries)

        dataset be like: 'mro/hirise/rdrv11'
        bbox: {'minlat': -0.5, 'maxlat': 0.5, 'westlon': 359.5, 'eastlon': 0.5}
        """

        assert all(k in bbox for k in ('minlat','maxlat','westlon','eastlon')), (
            "Expected 'bbox' with keys: 'minlat','maxlat','westlon','eastlon'"
        )

        req = request_products(bbox, self.target, self.host, self.instr, self.ptype, contains=contains)
        result = req.json()
        self._result = result
        status = result['ODEResults']['Status']
        if status.lower() != 'success':
            print('oops, request failed. check `result`')
        return req

    def count(self):
        if self._result is None:
            return None
        try:
            cnt = self._result['Count']
            return cnt
        except:
            return 0

    def read_products(self, request):
        products = read_products(request)
        return products

    def parse_products(self, products, schema):
        products_output = []
        for i,product in enumerate(products):
            _meta = readout_product_meta(product)
            _files = readout_product_files(product)
            _fprint = readout_product_footprint(product)
            _pfile = find_product_file(product_files=_files,
                                           product_type='product_image',
                                           descriptors=DESCRIPTORS[self.instr])
            _pfile = _pfile['URL']
            try:
                _lfile = find_product_file(product_files=_files,
                                               product_type='product_label',
                                               descriptors=DESCRIPTORS[self.instr])
                _lfile = _lfile['URL']
            except KeyError as err:
                _lfile = _pfile

            _dout = _meta
            _dout['geometry'] = _fprint
            _dout['image_url'] = _pfile
            _dout['label_url'] = _lfile
            products_output.append(_dout)

        print("{} products found".format(len(products_output)))
        return products_output


# ODEQuery.read_products
def read_products(request):
    assert request.status_code == 200 and request.json()['ODEResults']['Status'].lower() == 'success'
    try:
        products = request.json()['ODEResults']['Products']['Product']
        assert isinstance(products, list), "Was expecting 'list', got '{}' instead".format(type(products))
    except:
        log.info("No products were found")
        products = None
    return products


# USED by 'query_bbox'
def request_products(bbox, target=None, host=None, instr=None, ptype=None, contains=False):
    """
    bbox = {
        'minlat': [-65:65],
        'minlat': [-65:65],
        'westlon': [0:360],
        'eastlon': [0:360]
    }
    'ptype' (eg, "rdrv11") is used only when 'instr' is also defined (e.g, "hirise").
    """
    api_endpoint = API_URL

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
    if contains:
        payload.update({'loc':'o'})

    #payload.update({'pretty':True})
    return requests.get(api_endpoint, params=payload)


# USED by 'parse_products'
def readout_product_files(product_json):
    product_files = product_json['Product_files']['Product_file']
    return product_files


# USED by 'parse_products'
def readout_product_footprint(product_json):
    # 'Footprint_geometry' and 'Footprint_C0_geometry' may contain 'GEOMETRYCOLLECTION'
    # when the footprint cross the meridian in "c180" or "c0" frames
    #product_geom = request.json()['ODEResults']['Products']['Product']['Footprint_geometry']
    #product_geom = request.json()['ODEResults']['Products']['Product']['Footprint_C0_geometry']
    product_geom = product_json['Footprint_GL_geometry']
    return product_geom


# USED by 'parse_products'
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


# USED by 'parse_products'
def find_product_file(product_files, product_type, descriptors=DESCRIPTORS):
    _key,_val = descriptors[product_type]
    pfl = list(filter(lambda pf:pf[_key]==_val, product_files))
    _multiple_matches = "I was expecting only one Product matching ptype '{}' bu got '{}'."
    assert len(pfl) == 1, _multiple_matches.format(product_type, len(pfl))
    return pfl[0]


# USED by 'download.get_product'
def request_product(PRODUCTID, api_endpoint):
    payload = dict(
        query='product',
        results='fmp',
        output='JSON',
        productid=PRODUCTID
    )
    #payload.update({'pretty':True})
    return requests.get(api_endpoint, params=payload)


# def requested_product_files(request):
#     product_files = request.json()['ODEResults']['Products']['Product']['Product_files']['Product_file']
#     return product_files
