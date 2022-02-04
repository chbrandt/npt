import requests

from npt import log
# from npt import query
from npt import datasets

API_URL = 'https://oderest.rsl.wustl.edu/live2'

_DESCRIPTORS_TEMPLATE = {
    'product_image': ('Description', 'PRODUCT DATA FILE'),
    'product_label': ('Description', 'PRODUCT LABEL FILE'),
    'browse_image': ('Description', 'BROWSE IMAGE'),
    'browse_thumbnail': ('Description', 'THUMBNAIL IMAGE')
}

# FILTERS = {
#     'ctx': ("^(CRU|MOI|T01)_", False),
#     'hirise': ("^(PSP|ESP)_.*(RED)", True),
#     'hrsc': (".*_ND3.*", True)
# }

COORDS_REF = {
    'C0': 'Footprint_C0_geometry',  # -180:+180
    'C180': 'Footprint_GL_geometry' # 0:360
}

METADATA = [
    'Target_name',
    'Footprints_cross_meridian',
    'Map_scale',
    'Center_latitude',
    'Center_longitude',
    'Easternmost_longitude',
    'Westernmost_longitude',
    'Minimum_latitude',
    'Maximum_latitude',
    'Emission_angle',
    'Incidence_angle',
    'Phase_angle',
    'Solar_longitude',
    'Observation_time',
    'Product_creation_time',
    'UTC_start_time',
    'UTC_stop_time'
]

DB_ID = 'usgs_ode'


from collections import UserList

class ODEProducts(list):
    def __init__(self):
        super()

    def to_dataframe(self):
        import shapely
        import geopandas
        from copy import deepcopy

        products = []
        for prod in self:
            product = deepcopy(prod)
            try:
                _geom = shapely.wkt.loads(product['geometry'])
                if (type(_geom) == shapely.geometry.GeometryCollection
                    or type(_geom) == shapely.geometry.MultiPolygon):
                    _geom = _geom.envelope
                assert type(_geom) == shapely.geometry.Polygon
            # except TypeError as err:
            except Exception as err:
                print("Error in: ", product)
                _geom = None
            finally:
                product['geometry'] = _geom
            products.append(product)

        gdf = geopandas.GeoDataFrame(products)
        return gdf


class ODE(object):
    _result = None
    def __init__(self, dataset):
        """
        dataset string example: 'mars/mro/ctx/edr'
        """
        target, mission, instrument, product_type = dataset.split('/')
        assert dataset in datasets.list()
        self.dataset = dataset
        self.target = target
        self.mission = mission
        self.instr= instrument
        self.ptype = product_type

    def query(self, bbox, match='intersect', bbox_ref='C0'):
        """
        Return list of found products (in dictionaries)

        bbox: {'minlat': -0.5, 'maxlat': 0.5, 'westlon': 359.5, 'eastlon': 0.5}
        """

        assert all(k in bbox for k in ('minlat','maxlat','westlon','eastlon')), (
            "Expected 'bbox' with keys: 'minlat','maxlat','westlon','eastlon'"
        )

        contains = False if 'intersect' in match else True

        assert bbox_ref in COORDS_REF.keys()
        if bbox_ref == 'C0':
            bbox = bbox.copy()
            _wl = bbox['westlon']
            _el = bbox['eastlon']
            assert _wl < _el
            bbox['westlon'] = _wl+360 if _wl < 0 else _wl
            bbox['eastlon'] = _el+360 if _el < 0 else _el

        assert bbox['westlon'] < bbox['eastlon']

        req = request_products(bbox,
                                self.target,
                                self.mission,
                                self.instr,
                                self.ptype,
                                contains=contains)
        result = req.json()
        if result['ODEResults']['Status'].lower() != 'success':
            errmsg = result['ODEResults']['Error']
            print('Request failed:', str(errmsg))
        else:
            self._result = result
            self._ref_coords = bbox_ref

        return self

    def _count(self):
        if self._result is None:
            return None
        try:
            cnt = int(self._result['ODEResults']['Count'])
        except:
            print(self._result)
            raise
        return cnt

    def parse(self):
        if not self._result:
            return None
        if self._count() > 1:
            products = self._result['ODEResults']['Products']['Product']
        else:
            products = [self._result['ODEResults']['Products']['Product']]
        assert isinstance(products, list), "Was expecting 'list', got '{}' instead".format(type(products))
        if not products:
            print("No products found")
            return None

        products_output = ODEProducts()
        for i,product in enumerate(products):
            _meta = readout_product_meta(product)
            _files = readout_product_files(product)
            _fprint = readout_product_footprint(product, self._ref_coords)
            _pfile = find_product_file(product_files=_files,
                                       product_type='product_image',
                                       # descriptors=DESCRIPTORS[self.instr])
                                       descriptors=datasets.descriptors(self.dataset))
            _pfile = _pfile['URL']
            try:
                _lfile = find_product_file(product_files=_files,
                                           product_type='product_label',
                                           # descriptors=DESCRIPTORS[self.instr])
                                           descriptors=datasets.descriptors(self.dataset))
                _lfile = _lfile['URL']
            except KeyError as err:
                _lfile = None

            try:
                _bfile = find_product_file(product_files=_files,
                                           product_type='browse_image',
                                           # descriptors=DESCRIPTORS[self.instr])
                                           descriptors=datasets.descriptors(self.dataset))
                _bfile = _bfile['URL']
            except KeyError as err:
                _bfile = None

            _dout = _meta
            _dout['geometry'] = _fprint
            _dout['image_url'] = _pfile
            _dout['label_url'] = _lfile
            _dout['browse_url'] = _bfile

            # Apply filters to product-ID
            filters = datasets.filters(self.dataset)
            if (not filters) or select_product(_dout, filters['product-id']):
                products_output.append(_dout)

        print("{} products found".format(len(products_output)))
        return products_output


def select_product(meta, filter_rule):
    import re
    expression, present = filter_rule
    regex = re.compile(expression, re.IGNORECASE)
    product_id = meta['id']
    _match = regex.match(product_id)
    return bool(_match) is present

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
def readout_product_footprint(product_json, coords_ref):
    # 'Footprint_geometry' and 'Footprint_C0_geometry' may contain 'GEOMETRYCOLLECTION'
    # when the footprint cross the meridian in "c180" or "c0" frames
    #product_geom = request.json()['ODEResults']['Products']['Product']['Footprint_geometry']
    #product_geom = request.json()['ODEResults']['Products']['Product']['Footprint_C0_geometry']
    product_geom = product_json[COORDS_REF[coords_ref]]
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

    try:
        for key in METADATA:
            product[key] = product_json.get(key, None)
    except Exception as err:
        print(product_json)
        raise

    return product


# USED by 'parse_products'
def find_product_file(product_files, product_type, descriptors):
    desc_key, desc_val = descriptors[product_type]
    is_val_regex = desc_val.strip()[-1]=='*'
    desc_val_token = desc_val[:-1].strip()
    _foo = (lambda pf:
            pf[desc_key] == desc_val
            if not is_val_regex
            else
            desc_val_token in pf[desc_key])
    pfl = list(filter(_foo, product_files))
    multiple_matches = "I was expecting one Product matching ptype '{}' but got '{}' in {}"
    assert len(pfl) == 1, multiple_matches.format(product_type, len(pfl), product_files)
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
