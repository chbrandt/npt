import pytest
import os

from npt import download

from npt import log
log.setLevel('DEBUG')

_data = {
    'success': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/256px-The_Earth_seen_from_Apollo_17.jpg',
        'name': '256px-The_Earth_seen_from_Apollo_17.jpg'
    },
    'not_found': {
        'url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/not_found_pelamor.jpg',
        'name': None
    }
}


def _mktempdir():
    from tempfile import mkdtemp
    return mkdtemp()

def _rmtempdir(_dir):
    from shutil import rmtree
    rmtree(_dir)

def test_TestFunctions():
    _dir = _mktempdir()
    assert os.path.exists(_dir) and os.path.isdir(_dir)
    _rmtempdir(_dir)
    assert not os.path.exists(_dir)


def test_url():
    res = download.file(_data['success']['url'])
    assert res
    assert os.path.isfile(res)
    assert res == _data['success']['name']
    os.remove(res)


def test_url_notfound():
    _fn = _data['not_found']['url']
    res = download.file(_fn)
    assert res is None


def test_url_progressbar():
    res = download.file(_data['success']['url'], progress=True)
    assert res
    assert os.path.isfile(res)
    assert res == _data['success']['name']
    os.remove(res)


# TODO: this test shouldn't exist. "requests.get" + "check" should be done in one place in download.py
def test_url_notfound_progressbar():
    _fn = _data['not_found']['url']
    res = download.file(_fn, progress=True)
    assert res is None


def test_specify_filename():
    _fn = 'test_filename.ext'
    #
    res = download.file(_data['success']['url'], filename=_fn)
    #
    assert res
    assert res == _fn
    assert os.path.isfile(_fn)
    os.remove(res)


def test_existing_absolute_path():
    _dir = _mktempdir()
    _fn = os.path.join(_dir, _data['success']['name'])
    #
    res = download.file(_data['success']['url'], filename=_fn)
    #
    assert res
    assert os.path.isfile(res)
    assert os.path.dirname(res) == _dir
    _rmtempdir(_dir)


def test_nonexisting_path_create():
    # Default
    _dir = _mktempdir()
    _dir = os.path.join(_dir, 'nonexistent', 'directory')
    _fn = os.path.join(_dir, _data['success']['name'])
    #
    # By default, make the necessary path/directories (make_dirs=True)
    res = download.file(_data['success']['url'], filename=_fn)
    #
    assert res
    assert os.path.isfile(res)
    assert os.path.dirname(res) == _dir
    _rmtempdir(_dir)


def test_nonexisting_path_no_create():
    _dir = _mktempdir()
    _dirnon = os.path.join(_dir, 'nonexistent', 'directory')
    _fn = os.path.join(_dirnon, _data['success']['name'])
    #
    res = download.file(_data['success']['url'], filename=_fn, make_dirs=False)
    #
    assert res is None
    assert not os.path.isdir(_dirnon)
    _rmtempdir(_dir)


def test_file_already_downloaded():
    _dir = _mktempdir()
    _fn = os.path.join(_dir, _data['success']['name'])
    #
    res1 = download.file(_data['success']['url'], filename=_fn)
    res2 = download.file(_data['success']['url'], filename=_fn)
    #
    assert res1 == res2
    _rmtempdir(_dir)


def test_list_urls():
    _dir = _mktempdir()
    urls,names = list(zip(*[ (d['url'],d['name']) for d in _data.values() ]))
    #
    res = download.files(urls, path=_dir)
    #
    join = lambda d: os.path.join(_dir,d) if d else None
    exp = [ join(d) for d in names ]

    assert len(res) == len(exp)
    assert all([ res[i]==exp[i] for i in range(len(exp)) ])
    _rmtempdir(_dir)
