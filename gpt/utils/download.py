import os
import sys
import shutil
import requests

from ode import request_product
from ode import find_product_file


def download_file_silent(url, filename):
    """
    Download file (silently)

    Usage:
        download_file_silent('http://web4host.net/5MB.zip', 'local_filename.zip')
    """
    r = requests.get(url)
    with open(filename,'wb') as f:
        f.write(r.content)
    return


def download_file_progress(url, filename, verbose=False):
    """
    Download file with progressbar

    Usage:
        download_file_progress('http://web4host.net/5MB.zip', 'local_filename.zip')
    """
    import tqdm
    r = requests.get(url, stream=True)
    file_size = int(r.headers['Content-Length'])
    chunk = 1
    chunk_size=1024
    num_bars = int(file_size / chunk_size)
    if verbose:
        print(dict(file_size=file_size))
        print(dict(num_bars=num_bars))

    with open(filename, 'wb') as fp:
        for chunk in tqdm.tqdm(
                                    r.iter_content(chunk_size=chunk_size)
                                    , total= num_bars
                                    , unit = 'KB'
                                    , desc = filename
                                    , leave = True # progressbar stays
                                ):
            fp.write(chunk)
    return


def download_file(url, filename=None, progress_on=False):
    if not filename:
        local_filename = os.path.join('.', url.split('/')[-1])
    else:
        local_filename = filename

    print('--> Downloading file {} ..'.format(local_filename))
    if progress_on:
        download_file_progress(url, local_filename)
    else:
        download_file_silent(url, local_filename)
    print('--> File downloaded.'.format(local_filename))

    return local_filename


def download_files(urls, descriptors, filenames=None, path=None, progress_on=False):
    assert isinstance(urls, (list, tuple))
    assert isinstance(descriptors, (list, tuple))
    assert len(urls) == len(descriptors)

    if not filenames:
        path = path.strip() if path != None and len(path.strip()) > 0 else '.'
        filenames = [os.path.join(path, url.split('/')[-1]) for url in urls]

    assert len(filenames) == len(urls), "List of 'filenames' must match length of 'urls'"

    files_downloaded = {}
    for url, descriptor, filename in zip(urls,descriptors, filenames):
        try:
            _fn = download_file(url, filename, progress_on)
            files_downloaded[descriptor] = _fn
        except:
            pass

    return files_downloaded


def get_product(product_id, file_types, descriptors, api_endpoint, path=None, progress_on=True):
    pid = product_id

    base_path = path or '.'
    if not os.path.isdir(base_path):
        os.mkdir(base_path)

    print('Querying ODE for Product {} ..'.format(pid))
    req = request_product(pid, api_endpoint)
    if not req.status_code == 200:
        print('ODE query for product {} failed.'.format(pid), file=sys.stderr)
        return False

    available_files = req.json()['ODEResults']['Products']['Product']['Product_files']['Product_file']
    files_selected = [find_product_file(available_files, _ft, descriptors) for _ft in file_types]

    try:
        path = os.path.join(base_path, pid)
        if not os.path.isdir(path):
            os.mkdir(path)
        print('-> Downloading Image data and Browse products for {} ..'.format(pid))
        urls=[_fs['URL'] for _fs in files_selected]
        products_downloaded = download_files(urls=urls, descriptors=file_types, path=path, progress_on=progress_on)
        print('-> Data products downloaded.')
    except:
        print("-X ERROR while downloading '{pid}' products. Cleaning out path '{pid}'".format(pid=pid))
        shutil.rmtree(pid)

    print('Done.')
    return products_downloaded


def get_products(product_ids, file_types, descriptors, api_endpoint, path=None, progress_on=True):
    '''
    List of Product-IDs
    '''
    base_path = path or '.'
    products_data = {}
    pids = product_ids
    for i, pid in enumerate(product_ids):
        print('Get-Products: ({i}/{size}) {pid}'.format(i=i, size=len(pids), pid=pid))
        try:
            products_downloaded = get_product(pid,
                                              file_types=file_types,
                                              descriptors=descriptors,
                                              progress_on=progress_on,
                                              api_endpoint=api_endpoint,
                                              path=base_path)
            products_data[pid] = products_downloaded
        except:
            pass
        print('---')

    return products_data
