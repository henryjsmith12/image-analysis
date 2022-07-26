"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import numpy as np
import os
from spec2nexus import spec
import tifffile as tiff

# ----------------------------------------------------------------------------------

from imageanalysis.gridding import gridScan
from imageanalysis.mapping import mapScan

# ==================================================================================

class Project:
    """
    Contains a list of experimental scans and path variables.
    """
   
    def __init__(
        self, 
        project_path: str, 
        spec_path: str,
        instrument_path: str,
        detector_path: str
    ) -> None:
        
        # TODO: Check if paths are valid
        # TODO: Allow Pathlib paths

        if not [type(project_path), type(spec_path), type(instrument_path), 
        type(detector_path)] == [str, str, str, str]:
            raise TypeError("Paths must be of the type str")

        # Path variables
        self.path = project_path
        self.spec_path = spec_path
        self.instrument_path = instrument_path
        self.detector_path = detector_path

        self.spec_data = spec.SpecDataFile(spec_path)
        self.scan_numbers = self.spec_data.getScanNumbers()

        # List of Scan objects
        self.scans = [Scan(self.spec_data.getScan(i), project_path, spec_path, instrument_path, detector_path) for i in self.scan_numbers]

# ==================================================================================

class Scan:
    """
    Contains SPEC data, raw image data, and gridded image data.
    """

    def __init__(self, spec_scan, project_path, spec_path, instrument_path, detector_path) -> None:

        # Data variables
        self.spec_data = None
        self.raw_image_data = None
        self.reciprocal_space_map = None
        self.h_map, self.k_map, self.l_map = None, None, None
        self.gridded_image_data, self.gridded_image_coords = None, None
        self.h_grid_min, self.h_grid_max, self.h_grid_n = None, None, None
        self.k_grid_min, self.k_grid_max, self.k_grid_n = None, None, None
        self.l_grid_min, self.l_grid_max, self.l_grid_n = None, None, None

        self.spec_scan = spec_scan
        self.number = spec_scan.scanNum

        # Path variables
        self.project_path = project_path
        self.spec_path = spec_path
        self.instrument_path = instrument_path
        self.detector_path = detector_path
        self.raw_image_path = f"{project_path}/images/{os.path.basename(os.path.splitext(self.spec_path)[0])}/S{str(self.number).zfill(3)}"

        # Data processing
        self.spec_data = spec_scan.data
        
    # ------------------------------------------------------------------------------

    def getImageData(self):
        """
        Retrieves raw image data from path.
        """

        image_paths = sorted(os.listdir(self.raw_image_path))
        image_data = []

        monitor_norm_factors = self.spec_scan.data["Ion_Ch_2"] * 200000
        filter_norm_factors = self.spec_scan.data["transm"] * 1

        for i in range(len(image_paths)):
            img_basepath = image_paths[i]
            img_path = f"{self.raw_image_path}/{img_basepath}"
            img_array = tiff.imread(img_path).T
            img_array = img_array / (filter_norm_factors[i] * monitor_norm_factors[i])
            image_data.append(img_array)

        image_data = np.array(image_data)
        
        return image_data

    # ------------------------------------------------------------------------------

    def mapImageData(self):
        """
        Creates a reciprocal space map from raw image data.
        """

        rsm = mapScan(self.spec_scan, self.instrument_path, self.detector_path)

        self.reciprocal_space_map = rsm
        self.h_map = self.reciprocal_space_map[:, :, :, 0]
        self.k_map = self.reciprocal_space_map[:, :, :, 1]
        self.l_map = self.reciprocal_space_map[:, :, :, 2]
        self.h_grid_min, self.h_grid_max, self.h_grid_n = np.amin(self.h_map), np.amax(self.h_map), 250
        self.k_grid_min, self.k_grid_max, self.k_grid_n = np.amin(self.k_map), np.amax(self.k_map), 250
        self.l_grid_min, self.l_grid_max, self.l_grid_n = np.amin(self.l_map), np.amax(self.l_map), 250

    # ------------------------------------------------------------------------------

    def setGriddingParameters(self, 
        h_min, h_max, h_n,
        k_min, k_max, k_n,
        l_min, l_max, l_n
    ):
        """
        Sets HKL bounds and point count for gridding interpolation.
        """

        self.h_grid_min, self.h_grid_max, self.h_grid_n = float(h_min), float(h_max), int(h_n)
        self.k_grid_min, self.k_grid_max, self.k_grid_n = float(k_min), float(k_max), int(k_n)
        self.l_grid_min, self.l_grid_max, self.l_grid_n = float(l_min), float(l_max), int(l_n)

    # ------------------------------------------------------------------------------

    def gridImageData(self):
        """
        Creates a gridded image dataset from a reciprocal space map and raw image data.
        """
        hkl_min = (self.h_grid_min, self.k_grid_min, self.l_grid_min)
        hkl_max = (self.h_grid_max, self.k_grid_max, self.l_grid_max)
        hkl_n = (self.h_grid_n, self.k_grid_n, self.l_grid_n)

        self.gridded_image_data, self.gridded_image_coords = gridScan(
            self.raw_image_data, 
            self.reciprocal_space_map,
            (hkl_min, hkl_max, hkl_n)
        )

# ==================================================================================