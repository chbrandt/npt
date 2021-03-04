import pytest

import os
import json
import shutil
from pathlib import Path

from npt.isis import sh
from npt import utils
from npt import pipelines


_config = {
    'docker': {
        'processing': 'isis3_gdal_npt_tests'
    },
    'basedir': './tests/tmp'
}

_data = {
    'bbox': {
        'empty': {'minlat':0, 'maxlat':0, 'eastlon':0, 'westlon':0},
        'valid': {'minlat':-1, 'maxlat':1, 'westlon':359, 'eastlon':1}
    },
    'geojson_filename': None
}


def mktmppath(subdir=None, prefix=None):
    basedir = _config['basedir']
    basedir = basedir if not subdir else os.path.join(basedir, subdir)
    os.makedirs(basedir, exist_ok=True)

    if prefix is not None:
        assert isinstance(prefix, str)
        tmpdir = utils.tmpdir.mkpath(basedir=basedir, prefix=prefix)
        print(f"Create TMPDIR '{tmpdir}'")
    else:
        tmpdir = Path(basedir)

    return tmpdir


class TestSearch:

    def test_null(self):
        with pytest.raises(TypeError) as err:
            pipelines.search.run()

    def test_search_empty_bbox(self):
        bbox = _data['bbox']['empty']

        dset = 'mars/mro/ctx/edr'

        tmpdir = mktmppath('search_')
        ofile =  (tmpdir / 'output.json').as_posix()

        results = pipelines.search.run(bbox, dset, ofile, contains=False)
        #TODO: assert results != None
        assert results == None

        bbox = {}
        results = pipelines.search.run(bbox, dset, ofile, contains=False)
        assert results == None

        # shutil.rmtree(tmpdir.as_posix())

    def test_search_datasets(self):
        bbox = _data['bbox']['valid']

        dsets = [
            'mars/mro/hirise/rdrv11',
            'mars/mex/hrsc/rdrv3',
            'mars/mro/ctx/edr',
        ]

        tmpdir = mktmppath('search_')

        for dset in dsets:
            print(f"Test search dataset: '{dset}'")
            ofile =  (tmpdir / f"{dset.replace('/','_')}.json").as_posix()
            res_gdf = pipelines.search.run(bbox, dset, ofile, contains=False)
            res_prd = pipelines.search.run(bbox, dset, contains=False)

            # print(res_gdf)
            # print(json.dumps(res_prd, indent=2))

            assert len(res_gdf) > 0
            assert len(res_prd) > 0

            out_gson = json.loads(res_gdf.to_json())
            out_file = json.load(open(ofile, 'r'))

            assert isinstance(out_gson, dict) and isinstance(out_file, dict)
            assert 'features' in out_gson.keys()
            assert 'features' in out_file.keys()
            assert len(out_gson['features']) == len(out_file['features'])

            #TODO: check for features' properties (eg, 'image_path')

        # Persist last geojson for future tests (eg, download)
        _data['geojson_filename'] = ofile

        # shutil.rmtree(tmpdir.as_posix())


class TestDownload:

    def test_null(self):
        with pytest.raises(TypeError) as err:
            pipelines.download.run()

    def test_download_data_product(self):
        with open(_data['geojson_filename'],'r') as fp:
            _gson = json.load(fp)

        odir = mktmppath('download_')

        n_features = 1
        features = _gson['features'][:n_features]
        print(features)
        new_features = []
        for feature in features:
            print(feature)
            #TODO: Add option to download only certain data product types (e.g, "browse image")
            new_feature = pipelines.download.run(feature, odir, progressbar=True)
            print(new_feature)
            new_props = set(new_feature.keys()) - set(feature.keys())
            assert 'image_path' in new_feature['properties']
            assert os.path.exists(new_feature['properties']['image_path'])
            new_features.append(new_feature)

        _gson['features'] = new_features

        with open(_data['geojson_filename'],'w') as fp:
            json.dump(_gson, fp)


class TestProcessing:

    def test_null(self):
        with pytest.raises(TypeError) as err:
            pipelines.processing.run()

    def test_reduce_data_docker(self):
        with open(_data['geojson_filename'],'r') as fp:
            _gson = json.load(fp)

        if _config['docker'] and _config['docker']['processing']:
            _c = _config['docker']['processing']
            sh.set_docker(_c)
            print(f"Set to run container '{_c}'")

        odir = mktmppath('processing_')
        tmpdir = mktmppath(os.path.join('processing_','tmp'))

        n_features = 1
        features = _gson['features'][:n_features]
        print(features)
        new_features = []
        for feature in features:
            #TODO: Add argument to set the docker container (eg, 'isis3') to run
            new_feature = pipelines.processing.run(feature, odir, tmpdir=tmpdir)
            print(new_feature)
            new_features.append(new_feature)

        _gson['features'] = new_features

        with open(_data['geojson_filename'],'w') as fp:
            json.dump(_gson, fp)
