"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import matplotlib.pyplot as plt
import numpy as np
import os
import spec2nexus as s2n
from spec2nexus import spec

# ----------------------------------------------------------------------------------

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
        self.grid_dims = None

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
        self.raw_image_data = self.getImageData()
        self.reciprocal_space_map = self.mapImageData()
        self.h_map = self.reciprocal_space_map[:, :, :, 0]
        self.k_map = self.reciprocal_space_map[:, :, :, 1]
        self.l_map = self.reciprocal_space_map[:, :, :, 2]
        self.grid_dims = [250, 250, 250]

    # ------------------------------------------------------------------------------

    def getImageData(self):
        """
        Retrieves raw image data from path.
        """

        image_paths = sorted(os.listdir(self.raw_image_path))
        image_data = []

        for img_basepath in image_paths:
            img_path = f"{self.raw_image_path}/{img_basepath}"
            img_array = plt.imread(img_path)
            image_data.append(img_array)

        image_data = np.array(image_data)
        
        return image_data

    # ------------------------------------------------------------------------------

    def mapImageData(self):
        """
        Creates a reciprocal space map from raw image data.
        """

        rsm = mapScan(self.spec_scan, self.instrument_path, self.detector_path)

        return rsm

    # ------------------------------------------------------------------------------

    def gridImageData(self):
        """
        Creates a gridded image dataset from a reciprocal space map and raw image data.
        """
        
        ...

# ==================================================================================