# import ode

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

    query2geojson = run
    __call__ = run

    @staticmethod
    def query_footprints(bbox, dataset=None,
                         target='mars', host=None, instr=None, ptype=None):
        """
        Return list of found products (in dictionaries)

        dataset be like: 'mro/hirise/rdrv11'
        bbox: {'minlat': -0.5, 'maxlat': 0.5, 'westlon': 359.5, 'eastlon': 0.5}
        """

        # host,instr,ptype = dataset.split('/')
        #
        # assert all(k in bbox for k in ('minlat','maxlat','westlon','eastlon')), (
        #     "Expected 'bbox' with keys: 'minlat','maxlat','westlon','eastlon'"
        # )
        #
        # req = ode.request_products(ode.API_URL, bbox=bbox, target='mars', host=host, instr=instr, ptype=ptype)
        from .pds.ode import ODE

        if dataset:
            target,host,instr,ptype = dataset.split('/')

        ode = ODE(target,host,instr,ptype)

        req = ode.query_bbox(bbox)

        # products = ode.requested_products(req)
        products = ode.read_products(req)

        schema = {'meta':None, 'files':None, 'footprints':None}
        products = ode.parse_products(products, schema)
        return products



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


def _change_file_extension(filename, new_ext):
    fn = '.'.join(filename.split('.')[:-1] + [new_ext])
    return fn
def _add_file_subextension(filename, sub_ext):
    fs = filename.split('.')
    fs.insert(-1, sub_ext)
    fn = '.'.join(fs)
    return fn

class Processing:
    """
    Pre-processing (format+calibration+projection)

    Don't forget init-spice!
    """
    @staticmethod
    def run(filename_init, filename_result, projection="sinusoidal", tmpdir=None):
        # Create a temp dir for the processing
        import shutil
        import tempfile
        if tmpdir:
            assert os.path.isdir(tmpdir), """Given tmpdir '{}' does not exist""".format(tmpdir)
            tempfile.tempdir = tmpdir

        try:
            tmpdir = tempfile.mkdtemp(prefix='neanias_')
        except:
            print("Temporary directory ('{}') could not be created.".format(tmpdir))
            raise err
        else:
            print("Processing temporary dir: '{}'".format(tmpdir))

        try:
            f_in = shutil.copy(filename_init, tmpdir)

            # FORMAT (pds->isis)
            from gpt.isis import format
            # -- Init SPICE kernel
            format.init_spice(f_in)
            # -- Transfrom PDS (IMG) into ISIS (CUB) file
            f_cub = _change_file_extension(f_in, 'cub')
            format.pds2isis(f_in, f_cub)

            # CALIBRATION
            from gpt.isis import calibration
            f_cal = _add_file_subextension(f_cub, 'cal')
            calibration.radiometry(f_cub, f_cal)

            # MAP-PROJECTION
            from gpt.isis import projection
            ## Define projection
            f_map = _add_file_subextension(f_cal, 'map')
            _flist = [f_cal]
            proj_file = projection.define_projection(_flist, projection=projection, tmpdir=tmpdir)
            ## Project
            projection.map_project(f_cal, f_map, proj_file)

            # FORMAT to TIFF
            f_tif = _change_file_extension(f_map, 'tif')
            format.isis2tiff(f_map, f_tif)

        except Exception as err:
            print("OOOPS, something went wrong.")
            raise err
        finally:
            print("Cleaning temporary files/directory ({})".format(tmpdir))
            shutil.rmtree(tmpdir)


        # #calibration (radiometry)
        # #projection (image->map)
        # # SUBPRODUCTS (for future processing)
        # # ----------------------
        # #format (isis->tiff in 4326
        # try:
        #     Processing.proj_planet2earth(filetmp, fileout)
        # except:
        #     print("oops")
        # # HIGH_LEVEL PRODUCTS (for visualization)
        # return fileout

    @staticmethod
    def proj_planet2earth(filein, fileout):
        from gpt.raster import warp
        warp(filein, fileout)
