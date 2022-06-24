import os
# import rasterio
# import rioxarray
# from rioxarray import merge as rxmerge

from . import log


def copy_mean(merged_data, new_data, merged_mask, new_mask, **kwargs):
    return copy_(merged_data, new_data, merged_mask, new_mask,
        mean=True, **kwargs)


def copy_blend(merged_data, new_data, merged_mask, new_mask, **kwargs):
    return copy_(merged_data, new_data, merged_mask, new_mask,
        blend=True, **kwargs)


def copy_diff(merged_data, new_data, merged_mask, new_mask, **kwargs):
    return copy_(merged_data, new_data, merged_mask, new_mask,
        diff=True, **kwargs)


def copy_all(merged_data, new_data, merged_mask, new_mask, **kwargs):
    return copy_(merged_data, new_data, merged_mask, new_mask,
        diff=True, blend=True, mean=True, **kwargs)


def copy_(merged_data, new_data, merged_mask, new_mask,
          diff:bool=False, mean:bool=False, blend:bool=False,
          **kwargs):
    """
    Modify 'merged_data'
    """
    import numpy as np

    mask = np.empty_like(merged_mask, dtype="bool")
    np.logical_or(merged_mask, new_mask, out=mask)
    np.logical_not(mask, out=mask)

    if diff and mask.sum():
        # If 'diff', modify 'new_data' too!
        new_data = _diff(merged_data, new_data, mask)

    if mean:
        _mean(merged_data, new_data, mask)

    if blend:
        _blend(merged_data, new_data, mask)

    np.logical_not(new_mask, out=mask)
    np.logical_and(merged_mask, mask, out=mask)
    np.copyto(merged_data, new_data, where=mask, casting="unsafe")


def _blend(merged_data, new_data, mask, slope:str='gaussian', length:int=None):
    """
    Modify 'merged_data' by "blending" it to 'new_data' on difference slopes

    Input:
        slope: options are 'gaussian', 'uniform'
        length: size (in pixels) to smooth the slope (through the 'mask')
    """
    from scipy.ndimage import gaussian_filter, uniform_filter

    if slope == 'gaussian':
        _filter = gaussian_filter
    else:
        _filter = uniform_filter

    if not length:
        _size = min(mask.shape[1:])//3 # Make a large filter
    else:
        assert length > 1
        _size = int(length)

    weights = _filter(mask.astype(float), _size, mode='constant')
    weights = (weights - weights.min())/(weights.max() - weights.min())
    merged_data[mask] = (merged_data * (1 - weights) + new_data * weights)[mask]


def _mean(merged_data, new_data, mask):
    """
    Modify 'merged_data' with the average between merged_/new_data
    """
    import numpy as np

    _stack = np.stack([merged_data, new_data])
    merged_data[mask] = np.mean(_stack, axis=0)[mask]


def _diff(merged_data, new_data, mask):
    """
    Return 'new_data' + average difference between merged_/new_data
    """
    n_merged_data = merged_data[mask]
    n_new_data = new_data[mask]
    _mean = (n_merged_data - n_new_data).mean()
    return new_data + _mean


MERGE_METHODS = {
    'mean': copy_mean,
    'diff': copy_diff,
    'blend': copy_blend,
    'all': copy_all,
    'fast': copy_
}


def merge(filenames, output, nodata=None, method:str='all'):
    """
    Input:
        method: str
            How to resolve overlapping pixes.
            Options are: 'mean' and Rasterio's ('first,last, min, max')
            https://github.com/rasterio/rasterio/blob/master/rasterio/merge.py
    """
    from rioxarray import merge as rxmerge
    
    log.debug(f"Running '{merge.__name__}', from {__name__}")

    elements = []
    for file_ in filenames[::-1]:
        elements.append(rioxarray.open_rasterio(file_))

    method = MERGE_METHODS.get(method, method)
    merged = rxmerge.merge_arrays(elements, nodata=nodata, method=method)
    merged.rio.to_raster(output)
    return output
