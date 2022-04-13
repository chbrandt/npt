import os
import rasterio
import rioxarray

from . import log


def copy_mean(merged_data, new_data, merged_mask, new_mask, **kwargs):
    import numpy as np

    mask = np.empty_like(merged_mask, dtype="bool")
    np.logical_or(merged_mask, new_mask, out=mask)
    np.logical_not(mask, out=mask)

    #np.maximum(merged_data, new_data, out=merged_data, where=mask)
    _stack = np.stack([merged_data, new_data])
    merged_data[mask] = np.mean(_stack, axis=0)[mask]

    np.logical_not(new_mask, out=mask)
    np.logical_and(merged_mask, mask, out=mask)
    np.copyto(merged_data, new_data, where=mask, casting="unsafe")


def copy_shade(merged_data, new_data, merged_mask, new_mask, **kwargs):
    import numpy as np
    from scipy.ndimage import uniform_filter

    mask = np.empty_like(merged_mask, dtype="bool")
    np.logical_or(merged_mask, new_mask, out=mask)
    np.logical_not(mask, out=mask)

    #np.maximum(merged_data, new_data, out=merged_data, where=mask)
    _stack = np.stack([merged_data, new_data])
    # merged_data[mask] = np.mean(_stack, axis=0)[mask]
    weights = uniform_filter(mask.astype(float), 55, mode='constant')
    weights = (weights - weights.min())/(weights.max() - weights.min())
    merged_data[mask] = (merged_data*weights + new_data * (1 - weights))[mask]

    np.logical_not(new_mask, out=mask)
    np.logical_and(merged_mask, mask, out=mask)
    np.copyto(merged_data, new_data, where=mask, casting="unsafe")


MERGE_METHODS = {
    'mean': copy_mean
}


def merge(filenames, output, nodata=None, method:str='mean'):
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
