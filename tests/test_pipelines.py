import pytest

import os
import json
import shutil

from npt import pipelines
from npt import utils


def mktmppath():
    basedir = './tests/tmp'
    os.makedirs(basedir, exist_ok=True)
    tmpdir = utils.tmpdir.mkdir(basedir=basedir, prefix='npt_tests_')
    print(f"Create TMPDIR '{tmpdir}'")
    return tmpdir


class TestSearch:

    def test_null(self):
        with pytest.raises(TypeError) as err:
            pipelines.search.run()

    def test_search_empty_bbox(self):
        bbox = {'minlat':0, 'maxlat':0, 'eastlon':0, 'westlon':0}
        dset = 'mars/mro/ctx/edr'

        tmpdir = mktmppath()
        ofile =  (tmpdir / 'output.json').as_posix()

        results = pipelines.search.run(bbox, dset, ofile, contains=False)
        #TODO: assert results != None
        assert results == None

        bbox = {}
        results = pipelines.search.run(bbox, dset, ofile, contains=False)
        assert results == None

        shutil.rmtree(tmpdir.as_posix())

    def test_search_datasets(self):
        bbox = {'minlat':-1, 'maxlat':1, 'westlon':359, 'eastlon':1}

        dsets = [
            'mars/mro/ctx/edr',
            'mars/mex/hrsc/rdrv3',
            'mars/mro/hirise/rdrv11',
        ]

        tmpdir = mktmppath()

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

        shutil.rmtree(tmpdir.as_posix())


class TestDownload:

    def test_null(self):
        with pytest.raises(TypeError) as err:
            pipelines.download.run()

    def test_download_data_product(self):
        pass


class TestProcessing:

    def test_null(self):
        with pytest.raises(TypeError) as err:
            pipelines.processing.run()

    def test_process_data_product(self):
        pass
