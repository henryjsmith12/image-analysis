"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

import numpy as np
from spec2nexus import spec
import xrayutilities as xu

# ==================================================================================

def gridScan(
    raw_image_data: np.ndarray, 
    rsm: np.ndarray,
    gridding_params: tuple
):
    """
    Creates a gridded reciprocal space model of the raw image data.
    """

    h_min, k_min, l_min = gridding_params[0]
    h_max, k_max, l_max = gridding_params[1]
    h_n, k_n, l_n = gridding_params[2]

    h, k, l = rsm[:, :, :, 0], rsm[:, :, :, 1], rsm[:, :, :, 2]

    gridder = xu.Gridder3D(nx=h_n, ny=k_n, nz=l_n)
    gridder.KeepData(True)
    gridder.dataRange(
        xmin=h_min, xmax=h_max,
        ymin=k_min,ymax=k_max,
        zmin=l_min,zmax=l_max,
        fixed=True
    )
    gridder(h, k, l, raw_image_data)

    gridded_image_data = gridder.data
    coords = np.array([gridder.xaxis, gridder.yaxis, gridder.zaxis])

    print(gridded_image_data.shape)
    print(coords.shape)

    return gridded_image_data, coords

