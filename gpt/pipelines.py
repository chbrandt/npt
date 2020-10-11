import os

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
    def _run_geo_feature(geojson_feature, base_path, progressbar=False):
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
        product_feature = geojson_feature

        assert base_path, "Expected a valid path, got '{}' instead".format(base_path)

        properties = product_feature['properties']
        properties = Download.run_props(properties, base_path, progressbar)
        product_feature['properties'] = properties

        return product_feature

    run = _run_geo_feature


    @staticmethod
    def run_props(properties, base_path, progressbar=False):
        properties = properties.copy()

        image_url = properties['image_url']
        image_path = Download.download(image_url, basepath=base_path,
                                                  progressbar=progressbar)
        if image_path:
            properties['image_path'] = image_path

        if ('label_url' in properties
            and properties['label_url'] != properties['image_url']):
            label_url = properties['label_url']
            label_path = Download.download(label_url, basepath=base_path,
                                                      progressbar=progressbar)
            if label_path:
                properties['label_path'] = label_path

        return properties


    @staticmethod
    def download(url, basepath, progressbar=False):
        from .utils.download import download_file
        import os

        _file = url.split('/')[-1]
        file_path = os.path.join(basepath, _file)
        _out = download_file(url, filename=file_path, progress_on=progressbar)

        return file_path



def _change_file_extension(filename, new_ext):
    fn = '.'.join(filename.split('.')[:-1] + [new_ext])
    return fn
def _add_file_subextension(filename, sub_ext):
    fs = filename.split('.')
    fs.insert(-1, sub_ext)
    fn = '.'.join(fs)
    return fn
def _change_file_dirname(filename, new_dir):
    bn = os.path.basename(filename)
    fn = os.path.join(new_dir, bn)
    return fn

class Processing:
    """
    Pre-processing (format+calibration+projection)

    Don't forget init-spice!
    """
    @staticmethod
    def _run_geo_feature(geojson_feature, output_path, projection="sinusoidal", tmpdir=None):
        feature = geojson_feature.copy()
        result_filename = Processing._run_props(feature['properties'], output_path)
        return feature

    run = _run_geo_feature

    @staticmethod
    def _run_props(properties, output_path, map_projection, tmpdir):
        image_filename = properties['image_path']
        output = Processing.run_file(image_filename, output_path, map_projection, tmpdir)


    @staticmethod
    def run_file(filename_init, output_path, map_projection="sinusoidal", tmpdir=None):
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
            # -- Transfrom PDS (IMG) into ISIS (CUB) file
            f_cub = _change_file_extension(f_in, 'cub')
            format.pds2isis(f_in, f_cub)
            # -- Init SPICE kernel
            format.init_spice(f_cub)

            # CALIBRATION
            from gpt.isis import calibration
            f_cal = _add_file_subextension(f_cub, 'cal')
            calibration.radiometry(f_cub, f_cal)

            # MAP-PROJECTION
            from gpt.isis import projection
            ## Define projection
            f_map = _add_file_subextension(f_cal, 'map')
            _flist = [f_cal]
            proj_file = projection.define_projection(_flist, projection=map_projection, tmpdir=tmpdir)
            ## Project
            projection.map_project(f_cal, f_map, proj_file)

            # FORMAT to TIFF
            f_tif = _change_file_extension(f_map, 'tif')
            format.isis2tiff(f_map, f_tif)

        except Exception as err:
            print("OOOPS, something went wrong.")
            raise err
        else:
            print("Processing finished, file '{}' created.".format(f_tif))

        try:
            print("Copying from temp to archive/output path")
            f_out =  _change_file_dirname(f_tif, output_path)
            shutil.move(f_tif, f_out)
        except Exception as err:
            print("File '{}' could not be moved to '{}'".format(f_tif, f_out))
            print("Temporary files, '{}' will remain. Remove them manually.".format(tmpdir))
            raise err
        finally:
            print("Cleaning temporary files/directory ({})".format(tmpdir))
            shutil.rmtree(tmpdir)

        return f_out

    @staticmethod
    def proj_planet2earth(filein, fileout):
        from gpt.raster import warp
        warp(filein, fileout)
