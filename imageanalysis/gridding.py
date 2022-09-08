"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
import xrayutilities as xu


def gridScan(
    raw_image_data: np.ndarray,
    rsm: np.ndarray,
    grid_params: dict
) -> tuple:
    """Creates a gridded array of raw image data from RSM coordinates."""

    h_min = grid_params["H"]["min"]
    k_min = grid_params["K"]["min"]
    l_min = grid_params["L"]["min"]
    h_max = grid_params["H"]["max"]
    k_max = grid_params["K"]["max"]
    l_max = grid_params["L"]["max"]
    h_n = grid_params["H"]["n"]
    k_n = grid_params["K"]["n"]
    l_n = grid_params["L"]["n"]

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
