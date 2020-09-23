import ode

class Search:
    """
    Namespace only
    """
    @staticmethod
    def run(bounding_box, dataset_id, geojson_filename):
        """
        Write GeoJSON with products intersecting 'bounding_box'

        Inputs:
        * bounding_box:
            Dictionary with 'minlat','maxlat','westlon','eastlon' keys;
            Longitues range is [0:360] (180 center).
        * dataset_id:
            Datasets identifiers. Options are 'mro/ctx/edr', 'mro/hirise/rdrv11'.
        * geojson_filename:
            Filename for the GeoJSON containing found products as Features.
        """
        output_filename = geojson_filename
        products = Search.query_footprints(bbox=bounding_box,
                                           dataset=dataset_id)
        gdf = Search.write_geojson(products, filename=output_filename)
        return gdf


    @staticmethod
    def query_footprints(bbox, dataset):
        """
        Return list of found products (in dictionaries)

        dataset be like: 'mro/hirise/rdrv11'
        bbox: {'minlat': -0.5, 'maxlat': 0.5, 'westlon': 359.5, 'eastlon': 0.5}
        """

        host,instr,ptype = dataset.split('/')

        assert all(k in bbox for k in ('minlat','maxlat','westlon','eastlon')), (
            "Expected 'bbox' with keys: 'minlat','maxlat','westlon','eastlon'"
        )

        req = ode.request_products(ode.API_URL, bbox=bbox, target='mars', host=host, instr=instr, ptype=ptype)

        products = ode.requested_products(req)

        products_output = []
        for i,product in enumerate(products):
            _meta = ode.readout_product_meta(product)
            _files = ode.readout_product_files(product)
            _fprint = ode.readout_product_footprint(product)
            _pfile = ode.find_product_file(product_files=_files, product_type='product_image', descriptors=ode.DESCRIPTORS[instr])
            _pfile = _pfile['URL']
            try:
                _lfile = ode.find_product_file(product_files=_files, product_type='product_label', descriptors=ode.DESCRIPTORS[instr])
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


    @staticmethod
    def write_geojson(products, filename):
        """
        Write products to a GeoJSON 'filename'. Return GeoPandas dataframe.

        > Note: This function modifies field 'geometry' from 'products'

        products: list of product records (from search_footprints)
        filename: GeoJSON filename for the output
        """
        import geopandas as gpd
        import shapely

        assert isinstance(products, list), "Expected 'products' to be a list"
        assert filename and filename.strip() != '', "Give me a valid filename"

        for prod in products:
            try:
                prod['geometry'] = shapely.wkt.loads(prod['geometry'])
            except TypeError as err:
                print("Error in: ", prod)
                raise err

        gdf = gpd.GeoDataFrame(products)

        gdf.to_file(filename, driver='GeoJSON')
        print("File '{}' written.".format(filename))
        return gdf


class Download:
    @staticmethod
    def run(product_feature, base_path, progressbar=False):
        """
        Download data products (Image, Label) inside 'base_path'

        Inputs:
        * product_feature:
            Feature from GeoJSON from Search/Listing stage
            Field 'image_url' is expected, field 'image_path' will be added
            Field 'label_url' is optional, if present will be download also
        * base_path:
            Base filesystem path (directory) where product will be downloaded
        * progressbar (False):
            If a (tqdm) progress-bar should show download progress
        """
        assert base_path, "Expected a valid path, got '{}' instead".format(base_path)

        _properties = product_feature['properties']

        image_url = _properties['image_url']
        image_path = Download.download(image_url,
                                       basepath=base_path,
                                       progressbar=progressbar)
        if image_path:
            _properties['image_path'] = image_path

        if ('label_url' in _properties
            and _properties['label_url'] != _properties['image_url']):
            label_url = _properties['label_url']
            label_path = Download.download(label_url,
                                           basepath=base_path,
                                           progressbar=progressbar)
            if label_path:
                _properties['label_path'] = label_path

        return product_feature


    @staticmethod
    def download(url, basepath, progressbar=False):
        from download import download_file
        import os
        _file = url.split('/')[-1]
        file_path = os.path.join(basepath, _file)
        try:
            download_file(url, filename=file_path, progress_on=progressbar)
            return file_path
        except:
            return None
