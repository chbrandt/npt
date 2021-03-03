import pytest

from npt.search import ode
from npt import cli


expected_results = {
    'bbox_small': {
        'ctx': {
            'contain': {
                'ODEResults': {'Count': '1', 'Products': {'Product': {'BB_georeferenced': 'True', 'Center_georeferenced': 'True', 'Center_latitude': '0.0198', 'Center_longitude': '0', 'Comment': 'Meridiani Planum', 'Data_Set_Id': 'MRO-M-CTX-2-EDR-L0-V1.0', 'Easternmost_longitude': '359.82', 'Emission_angle': '0.2', 'External_url': 'https://pds-imaging.jpl.nasa.gov/pds/prod?q=OFSN+%3D/data/mro/mars_reconnaissance_orbiter/ctx/mrox_0433/data/P16_007361_1800_XN_00S000W.IMG+AND+RT+%3D+PDS_ZIPN', 'External_url2': 'http://viewer.mars.asu.edu/planetview/inst/ctx/P16_007361_1800_XN_00S000W#start', 'FilesURL': 'https://ode.rsl.wustl.edu/mars/productfiles.aspx?product_id=P16_007361_1800_XN_00S000W&product_idGeo=9083270', 'Footprint_C0_geometry': 'POLYGON ((0.18 0.4052, 0.27 -0.3064, -0.18 -0.3657, -0.26 0.3558, 0.18 0.4052))', 'Footprint_geometry': 'GEOMETRYCOLLECTION (POLYGON ((360 -0.342, 359.82 -0.3657, 359.74 0.3558, 360 0.385, 360 -0.342)), POLYGON ((0.18 0.4052, 0.27 -0.3064, 0 -0.342, 0.18 0.4052)))', 'Footprint_GL_geometry': 'POLYGON ((0.18 0.4052, 0.27 -0.3064, 359.82 -0.3657, 359.74 0.3558, 0.18 0.4052))', 'Footprint_NP_geometry': 'MULTIPOLYGON EMPTY', 'Footprint_souce': 'PDS Archive Index Table', 'Footprint_SP_geometry': 'MULTIPOLYGON EMPTY', 'Footprints_cross_meridian': 'True', 'ihid': 'MRO', 'iid': 'CTX', 'Incidence_angle': '44.11', 'LabelFileName': 'p16_007361_1800_xn_00s000w.img', 'LabelURL': 'https://pds-imaging.jpl.nasa.gov/data/mro/mars_reconnaissance_orbiter/ctx/mrox_0433/data/P16_007361_1800_XN_00S000W.IMG', 'Map_scale': '5.34', 'Maximum_latitude': '0.4052', 'Minimum_latitude': '-0.3657', 'Observation_time': '2008-02-21T00:58:55.697', 'ODE_notes': {'ODE_note': ['NOTE: Product Type set by ODE', 'NOTE: Instrument Host Id set by ODE', 'NOTE: No SC Clock Stop Count so SC Clock Start Count used for Stop Count', 'NOTE: Label keyword Orbit number value used for start orbit number value', 'NOTE: Label keyword Orbit number value used for stop orbit number value', 'NOTE: Observation time set to mid-point between start time and stop time', 'NOTE: Index Record:', '"MROX_0433","DATA/P16_007361_1800_XN_00S000W.IMG","4A_04_102202D500","P16_007361_1800_XN_00S000W","2008-02-21T00:58:48.971","CTX   ","NIFL ",5056,  7168, 1,    5.34,  1.14,  0.20, 44.11, 43.91,360.00,  0.02,  0.18, -0.37,359.73, -0.31,  0.26,  0.36,359.82,  0.41,"PSP       ","MARS  ","0888022748:232 ",292.8,   1.877,"195/238/229",   0,  26.74,   43.40, 266.93,3663.12, 266.93,"N",277.00,207.64, 42.25, 14.22,  0.01,  0.03,244340641.9, 34.81,14.83, 90.1,"Meridiani Planum                                                                ","OK    ",  7361', 'NOTE: Map scale set from index table entry', 'NOTE: Emission angle set from index table entry', 'NOTE: Incidence angle set from index table entry', 'NOTE: Phase set from index table entry', 'NOTE: Solar distance set from index table entry', 'NOTE: Solar longitude set from index table entry', 'NOTE: CTX location data updated from index table entry']}, 'pdsid': 'P16_007361_1800_XN_00S000W', 'PDSVolume_Id': 'MROX_0433', 'Phase_angle': '43.91', 'Pole_state': 'none', 'Producer_id': 'MRO_CTX_TEAM', 'Product_creation_time': '2008-07-17T04:09:49.000', 'Product_files': {'Product_file': [{'Description': 'PRODUCT DATA FILE WITH LABEL', 'FileName': 'P16_007361_1800_XN_00S000W.IMG', 'KBytes': '35001', 'Type': 'Product', 'URL': 'https://pds-imaging.jpl.nasa.gov/data/mro/mars_reconnaissance_orbiter/ctx/mrox_0433/data/P16_007361_1800_XN_00S000W.IMG'}, {'Description': 'BROWSE IMAGE', 'FileName': 'P16_007361_1800_XN_00S000W.IMG.JPEG', 'KBytes': '12', 'Type': 'Browse', 'URL': 'https://pds-imaging.jpl.nasa.gov/data/mro/mars_reconnaissance_orbiter/ctx/mrox_0433/extras/browse/P16_007361_1800_XN_00S000W.IMG.jpeg'}, {'Description': 'THUMBNAIL IMAGE', 'FileName': 'P16_007361_1800_XN_00S000W.IMG.JPEG_SMALL', 'KBytes': '1', 'Type': 'Browse', 'URL': 'https://pds-imaging.jpl.nasa.gov/data/mro/mars_reconnaissance_orbiter/ctx/mrox_0433/extras/thumbnail/P16_007361_1800_XN_00S000W.IMG.jpeg_small'}, {'Creation_date': '2020-01-15T21:11:26.016', 'Description': 'PRODUCT KML FILE <A HREF="PAGEHELP/QUICKSTARTGUIDE/ABOUTFOOTPRINTS.HTM" TARGET="_BLANK">HELP</A>', 'FileName': 'P16_007361_1800_XN_00S000W_IMG.KML', 'KBytes': '3', 'Type': 'Derived', 'URL': 'https://ode.rsl.wustl.edu/mars/datafile/kmlfiles/mro-m-ctx-2-edr-l0-v1/mrox_0433/data/p16_007361_1800_xn_00s000w_img.kml'}, {'Creation_date': '2020-01-15T21:11:25.930', 'Description': 'PRODUCT FOOTPRINT SHAPEFILES (TAR.GZ) <A HREF="PAGEHELP/QUICKSTARTGUIDE/ABOUTFOOTPRINTS.HTM" TARGET="_BLANK">HELP</A>', 'FileName': 'P16_007361_1800_XN_00S000W_IMG.TAR.GZ', 'KBytes': '4', 'Type': 'Derived', 'URL': 'https://ode.rsl.wustl.edu/mars/datafile/shapefiles/mro-m-ctx-2-edr-l0-v1/mrox_0433/data/p16_007361_1800_xn_00s000w_img.tar.gz'}, {'Creation_date': '2020-01-15T21:11:25.832', 'Description': 'PRODUCT FOOTPRINT SHAPEFILES (ZIP) <A HREF="PAGEHELP/QUICKSTARTGUIDE/ABOUTFOOTPRINTS.HTM" TARGET="_BLANK">HELP</A>', 'FileName': 'P16_007361_1800_XN_00S000W_IMG.ZIP', 'KBytes': '29', 'Type': 'Derived', 'URL': 'https://ode.rsl.wustl.edu/mars/datafile/shapefiles/mro-m-ctx-2-edr-l0-v1/mrox_0433/data/p16_007361_1800_xn_00s000w_img.zip'}]}, 'ProductURL': 'https://ode.rsl.wustl.edu/mars/indexproductpage.aspx?product_id=P16_007361_1800_XN_00S000W&product_idGeo=9083270', 'pt': 'EDR', 'RelativePathtoVol': 'data\\', 'Solar_distance': '244340641.9', 'Solar_longitude': '34.81', 'SpaceCraft_clock_start_count': '0888022748:232', 'SpaceCraft_clock_stop_count': '0888022748:232', 'Start_orbit_number': '7361', 'Stop_orbit_number': '7361', 'Target_name': 'MARS', 'UTC_start_time': '2008-02-21T00:58:48.971', 'UTC_stop_time': '2008-02-21T00:59:02.424', 'Westernmost_longitude': '0.18'}}, 'QuerySummary': {'Date': '2020-11-24T13:25:48.247', 'easternlon': '1', 'ihid': 'mro', 'iid': 'ctx', 'loc': 'o', 'maxlat': '1', 'minlat': '-1', 'output': 'JSON', 'pt': 'edr', 'query': 'PRODUCT', 'Query_Elapsed_Time': '00:00:00.2499868', 'results': 'FMPC', 'target': 'mars', 'westernlon': '359'}, 'Status': 'Success'}
            }
        }
    }
}


@pytest.fixture
def bbox_empty():
    return {'minlat':0, 'maxlat':0, 'eastlon':0, 'westlon':0}

@pytest.fixture
def bbox_small():
    return {'minlat':-1, 'maxlat':1, 'westlon':359, 'eastlon':1}

@pytest.fixture
def dataset_ctx():
    return 'mars/mro/ctx/edr'


class TestCLI:
    def test_empty_arguments(self):
        res = cli._search()
        assert res == False

    def test_bbox_empty(self, bbox_empty, dataset_ctx):
        res = cli._search(bbox=bbox_empty, dataset=dataset_ctx)
        assert res is None


class TestODE:
    partial_results = {}

    # def test_payload_setup(self, bbox_small, dataset_ctx):
    #     payload = ode._set_payload(bbox_small,
    #                                 dataset_ctx.split('/'),
    #                                 how='contain')
    #     print(payload)

    def test_bbox_empty(self, bbox_empty, dataset_ctx):
        res = ode.bounding_box(bbox_empty, dataset=dataset_ctx)
        assert res is None

    def test_bbox_small_contain(self, bbox_small, dataset_ctx):
        res = ode.bounding_box(bbox_small, dataset=dataset_ctx, how='contains')
        assert res['ODEResults']['Status'].lower() == 'success'
        assert int(res['ODEResults']['Count']) == 1
        assert isinstance(res['ODEResults']['Products'], dict)
        assert res['ODEResults']['QuerySummary']['query'].lower() == 'product'
        self.partial_results['bbox_small_contain'] = res

    def test_parse_results_bbox_small_contain(self, dataset_ctx):
        odejson = self.partial_results['bbox_small_contain']
        print(type(odejson), odejson)
        res = ode.parse_products(odejson, ode.DESCRIPTORS[dataset_ctx])
        assert len(res) == 1
