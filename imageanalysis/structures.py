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

# ==================================================================================

class Project:
   
    def __init__(
        self, 
        project_path: str, 
        spec_path: str,
        instrument_path: str,
        detector_path: str
    ) -> None:
            
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

        self.scans = [Scan(self.spec_data.getScan(i), project_path, spec_path) for i in self.scan_numbers]

# ==================================================================================

class Scan:

    def __init__(self, spec_scan, project_path, spec_path) -> None:

        self.spec_data = None
        self.raw_image_data = None
        self.reciprocal_space_map = None
        self.gridded_image_data, self.gridded_image_coords = None, None

        self.spec_scan = spec_scan
        self.number = spec_scan.scanNum
        self.project_path = project_path
        self.spec_path = spec_path
        self.raw_image_path = f"{project_path}/images/{os.path.basename(os.path.splitext(self.spec_path)[0])}/S{str(self.number).zfill(3)}"

        self.spec_data = spec_scan.data
        self.raw_image_data = self.getImageData()
        self.reciprocal_space_map = self.mapImageData()

    # ------------------------------------------------------------------------------

    def getImageData(self):
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
        ...

    # ------------------------------------------------------------------------------

    def gridImageData(self):
        ...

# ==================================================================================