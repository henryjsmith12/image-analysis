"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
import xrayutilities as xu


# TODO: Basic testing
# TODO: Find replacement for current gridding_params format
# TODO: Return coords as a list
# TODO: Make arbitrary enough to use as a static function
def gridScan(
    raw_image_data: np.ndarray,
    rsm: np.ndarray,
    gridding_params: tuple
) -> tuple:
    """Creates a gridded array of raw image data from RSM coordinates."""

    h_min, k_min, l_min = gridding_params[0]
    h_max, k_max, l_max = gridding_params[1]
    h_n, k_n, l_n = gridding_params[2]

    # Splits RSM into separate maps for H, K, and L coordinates
    h, k, l = rsm[:, :, :, 0], rsm[:, :, :, 1], rsm[:, :, :, 2]

    # Process for gridding image data with given bounds and pixel counts
    gridder = xu.Gridder3D(nx=h_n, ny=k_n, nz=l_n)
    gridder.KeepData(True)
    gridder.dataRange(
        xmin=h_min, xmax=h_max,
        ymin=k_min, ymax=k_max,
        zmin=l_min, zmax=l_max,
        fixed=True
    )
    gridder(h, k, l, raw_image_data)

    # gridded_image_data.shape: (h_n, k_n, l_n)
    # coords.shape: (3, length)
    gridded_image_data = gridder.data
    coords = np.array([gridder.xaxis, gridder.yaxis, gridder.zaxis])

    return gridded_image_data, coords
