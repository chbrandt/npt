import requests
from npt import log
from npt import datasets


DB_ID = 'usgs_ode'

API_URL = 'https://oderest.rsl.wustl.edu/live2'

COORDS_REF = {
    'C0': 'Footprint_C0_geometry',  # -180:+180
    'C180': 'Footprint_GL_geometry' # 0:360
}

METADATA = [
    'Target_name',
    'Footprints_cross_meridian',
#    'Map_resolution'
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
            except Exception as err:
                print("Error in: ", product)
                _geom = None
            finally:
                product['geometry'] = _geom
            products.append(product)

        gdf = geopandas.GeoDataFrame(products)
        return gdf


class ODE(object):
    """
    Handles querying ODE, and then parsing the results for a given dataset

    Check 'npt.datasets.list' for the available/supported datasets
    """
    _result = None # Cache ODE query results
    _ref_coords = 'C0'

    def __init__(self, dataset):
        """
        dataset string example: 'mars/mro/ctx/edr'
        """
        target, mission, instrument, product_type = dataset.split('/')
        assert dataset in datasets.list(), f"Dataset '{dataset}' not recognised."
        self.dataset = dataset
        self.target = target
        self.mission = mission
        self.instr= instrument
        self.ptype = product_type

    def query_bbox(self, bbox, match='intersect', bbox_ref='C0'):
        """
        Return list of found products (in dictionaries)

        bbox: {'minlat': -0.5, 'maxlat': 0.5, 'westlon': 359.5, 'eastlon': 0.5}
        """

        assert all(k in bbox for k in ('minlat','maxlat','westlon','eastlon')), (
            "Expected 'bbox' with keys: 'minlat','maxlat','westlon','eastlon'"
        )

        contains = False if 'intersect' in match else True

        assert bbox_ref in COORDS_REF.keys()
        assert bbox['westlon'] < bbox['eastlon'], bbox
        if bbox_ref == 'C0':
            bbox = bbox.copy()
            _wl = bbox['westlon']
            _el = bbox['eastlon']
            assert _wl < _el
            bbox['westlon'] = _wl+360 if _wl < 0 else _wl
            bbox['eastlon'] = _el+360 if _el < 0 else _el


        req = request_products(bbox,
                                self.target,
                                self.mission,
                                self.instr,
                                self.ptype,
                                contains=contains)

        result = req.json()
        log.debug(f"ODE results: {result}")

        if result['ODEResults']['Status'].lower() != 'success':
            errmsg = result['ODEResults']['Error']
            log.info('Request failed:', str(errmsg))
        else:
            self._result = result
            self._ref_coords = bbox_ref

        return self

    query = query_bbox

    def query_pid(self, product_id):
        """
        Return product_id if found
        """
        req = request_product(product_id,
                                self.target,
                                self.mission,
                                self.instr,
                                self.ptype)

        result = req.json()
        log.debug(f"ODE results: {result}")

        if result['ODEResults']['Status'].lower() != 'success':
            errmsg = result['ODEResults']['Error']
            log.info('Request failed:', str(errmsg))
        else:
            self._result = result

        return self


    def _count(self):
        """
        Number of products found
        """
        if self._result is None:
            return None
        try:
            cnt = int(self._result['ODEResults']['Count'])
        except:
            print(self._result)
            raise
        return cnt

    def parse(self):
        """
        Parse ODE results into a table/dataframe with columns from METADATA
        """
        if not self._result or not self._count():
            return None
        log.debug("Search results:", self._result)

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
            _meta = readout_product_meta(product, metadata=METADATA)
            _fprint = readout_product_footprint(product, self._ref_coords)

            files_obj = readout_product_files(product)

            _pobj = find_product_file(product_files=files_obj,
                                       product_type='product_image',
                                       descriptors=datasets.descriptors(self.dataset))
            _pfile = _pobj['URL']
            _psize = _pobj['KBytes']

            try:
                _lobj = find_product_file(product_files=files_obj,
                                           product_type='product_label',
                                           descriptors=datasets.descriptors(self.dataset))
                _lfile = _lobj['URL']
            except KeyError as err:
                _lfile = None

            try:
                _bobj = find_product_file(product_files=files_obj,
                                           product_type='browse_image',
                                           # descriptors=DESCRIPTORS[self.instr])
                                           descriptors=datasets.descriptors(self.dataset))
                _bfile = _bobj['URL']
            except KeyError as err:
                _bfile = None

            _dout = _meta
            _dout['geometry'] = _fprint
            _dout['image_url'] = _pfile
            _dout['image_kbytes'] = _psize
            _dout['label_url'] = _lfile
            _dout['browse_url'] = _bfile

            # Apply filters to product-ID (see npt.dataset._datasets)
            filters = datasets.filters(self.dataset)
            if (not filters) or select_product(_dout, filters['product-id']):
                products_output.append(_dout)

        log.info("{} products found".format(len(products_output)))
        return products_output


def select_product(meta, filter_rule):
    """
    The filter rules are (<regex>,<bool>), return (bool) if regex is/not in 'meta'
    """
    import re
    expression, present = filter_rule
    regex = re.compile(expression, re.IGNORECASE)
    product_id = meta['id']
    _match = regex.match(product_id)
    return bool(_match) is present


def request_product(product_id, target:str=None, host:str=None,
                    instr:str=None, ptype:str=None):
    """
    Return results for 'product_id' (if found)
    """
    payload = _payload_request(target, host, instr, ptype)

    payload.update({ 'pdsid': product_id })

    return _request_payload(payload)


def request_products(bbox:dict,
                     target:str=None, host:str=None,
                     instr:str=None, ptype:str=None,
                     contains:bool=False):
    """
    Assemble query-URL and (GET) request ODE server.

    ODE gets longitudes in the range [0:360]. Target, host, instr, ptype are as
    in 'npt.datasets.list'.

    bbox = {
        'minlat': <-65:65>,
        'maxlat': <-65:65>,
        'westlon': <0:360>,
        'eastlon': <0:360>
    }
    """
    payload = _payload_request(target, host, instr, ptype)

    payload.update(dict(
        minlat=bbox['minlat'],
        maxlat=bbox['maxlat'],
        westlon=bbox['westlon'],
        eastlon=bbox['eastlon']
    ))

    if contains:
        payload.update({'loc':'o'})

    return _request_payload(payload)


def _request_payload(payload):
    """
    Return result from (GET) request 'payload'
    """
    return requests.get(API_URL, params=payload)


def _payload_request(target:str, host:str, instr:str, ptype:str):
    """
    Assemble query-URL and (GET) request ODE server.
    """
    #    https://oderest.rsl.wustl.edu/live2/?
    # target=mars&
    # query=product&
    # results=fpcm&
    # output=XML&
    # pt=RDRV11&
    # iid=HiRISE&
    # ihid=MRO&
    payload = dict(
        query='product',
        results='fmpc',
        output='JSON',
        loc='f'
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
    return payload


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
def readout_product_meta(product_json:dict, metadata=METADATA) -> dict:
    """
    Return "{k:v}" filtered by 'metadata', plus 'id, mission, inst, type' fields

    Example:
        product_json = {}
    """
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
        for key in metadata:
            product[key] = product_json.get(key, None)
    except Exception as err:
        print(product_json)
        raise

    return product


# USED by 'parse_products'
def find_product_file(product_files:list, product_type:str, descriptors:dict) -> dict:
    """
    Return product from 'product_files' matching the "key,value" defined in 'descriptors[product_type]'
    (See npt.datasets._datasets)
    """
    desc_key, desc_val = descriptors[product_type]
    is_val_regex = desc_val.strip()[-1]=='*'
    desc_val_token = desc_val[:-1].strip()
    _foo = (lambda pf:
            pf[desc_key] == desc_val
            if not is_val_regex
            else desc_val_token in pf[desc_key]
            )
    pfl = list(filter(_foo, product_files))
    multiple_matches = "I was expecting one Product matching ptype '{}' but got '{}' in {}"
    assert len(pfl) == 1, multiple_matches.format(product_type, len(pfl), product_files)
    return pfl[0]
