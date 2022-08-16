"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import os

import matplotlib.pyplot as plt
import numpy as np
from spec2nexus import spec
import tifffile as tiff

from imageanalysis import io
from imageanalysis.gridding import gridScan
from imageanalysis.mapping import mapScan


# TODO: Allow Pathlib paths
# TODO: Basic testing
# TODO: Validate scan number exists
class Project:
    """Houses SPEC/XML filepaths and Scans."""

    def __init__(
        self,
        project_path: str,
        spec_path: str,
        instrument_path: str,
        detector_path: str
    ) -> None:

        filepath_types = [
            type(project_path),
            type(spec_path),
            type(instrument_path),
            type(detector_path)
        ]
        if filepath_types != [str, str, str, str]:
            raise TypeError("Filepaths must be of the type str.")

        # Checks for valid SPEC file
        if not io.isValidSPECFile(spec_path):
            raise TypeError("Invalid SPEC file.")

        # Checks for valid instrument configuration file
        if not io.isValidInstrumentXMLFile(instrument_path):
            raise TypeError("Invalid instrument configuration file.")

        # Checks for valid detector configuration file
        if not io.isValidDetectorXMLFile(detector_path):
            raise TypeError("Invalid detector configuration file.")

        # Path variables
        self.path = project_path
        self.spec_path = spec_path
        self.instrument_path = instrument_path
        self.detector_path = detector_path

        # Directory with scan image subdirectories
        # Basename matches spec file basename
        # Contents: "S001", "S002", etc.
        spec_basename = os.path.basename(os.path.splitext(self.spec_path)[0])
        self.spec_image_path = f"{project_path}/images/{spec_basename}"

        # Spec data object
        self.spec_data = spec.SpecDataFile(spec_path)

        # Scan number from spec data
        self.scan_numbers = self.spec_data.getScanNumbers()

        # List of Scan objects
        self.scans = []

        # Checks for image subdirectories present
        # It is okay to have a subset of the image subdirectories SPEC expects
        # Only the present subdirectories will be loaded
        for path in os.listdir(self.spec_image_path):
            if not path.startswith('.') and str.isdigit(path[1:]):

                # Retrieves scan number
                i = int(path[1:])
                scan = Scan(
                    spec_scan=self.spec_data.getScan(i),
                    project_path=project_path,
                    spec_path=spec_path,
                    instrument_path=instrument_path,
                    detector_path=detector_path
                )

                # Checks if expected raw image directory exists
                if os.path.exists(scan.raw_image_path):
                    self.scans.append(scan)

        # Updates numbers to only include scans with present image directories
        self.scan_numbers = [scan.number for scan in self.scans]


# TODO: Create a data structure class to properly organize raw/gridded data
class Scan:
    """Houses SPEC data and image data for a single scan."""

    def __init__(
        self,
        spec_scan: spec.SpecDataFileScan,
        project_path: str,
        spec_path: str,
        instrument_path: str,
        detector_path: str
    ) -> None:

        # Data variables
        self.spec_data = None
        self.raw_image_data = None
        self.reciprocal_space_map = None
        self.h_map, self.k_map, self.l_map = None, None, None
        self.gridded_image_data, self.gridded_image_coords = None, None

        # Gridding variables
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

        # Raw image directory
        spec_basepath = os.path.basename(os.path.splitext(self.spec_path)[0])
        raw_image_basepath = f"S{str(self.number).zfill(3)}"
        self.raw_image_path = f"{project_path}/images/{spec_basepath}/" \
            f"{raw_image_basepath}"

        # SPEC data
        self.spec_data = spec_scan.data

    # TODO: Check if path contents are valid
    def getImageData(self) -> np.ndarray:
        """Retrieves raw image data from path."""

        # Images sorted alphabetically
        image_paths = sorted(os.listdir(self.raw_image_path))
        image_data = []

        # Retrieves normalization factors from SPEC
        monitor_norm_factors = self.spec_scan.data["Ion_Ch_2"] * 200000
        filter_norm_factors = self.spec_scan.data["transm"] * 1

        # TODO: Check if item is an image path with valid dims
        i = 0
        for path in image_paths:
            path = image_paths[i]
            if (
                not path.startswith(".") and
                not path.startswith("alignment") and
                path.endswith("tif")
            ):
                img_basepath = path
                img_path = f"{self.raw_image_path}/{img_basepath}"

                # TODO: Replace this hack with proper image type checking
                try:
                    img_array = tiff.imread(img_path).T
                except:
                    img_array = plt.imread(img_path).T

                # Normalizes image
                norm_factor = filter_norm_factors[i] * monitor_norm_factors[i]
                img_array = img_array / norm_factor

                image_data.append(img_array)
                i += 1

        image_data = np.array(image_data)

        # TODO: Validate returned dims
        return image_data

    def mapImageData(self) -> None:
        """Creates a reciprocal space map from given parameters"""

        # TODO: Validate RSM dims
        self.reciprocal_space_map = mapScan(
            spec_scan=self.spec_scan,
            instrument_path=self.instrument_path,
            detector_path=self.detector_path
        )

        # TODO: Rework gridding parameter format
        self.h_map = self.reciprocal_space_map[:, :, :, 0]
        self.k_map = self.reciprocal_space_map[:, :, :, 1]
        self.l_map = self.reciprocal_space_map[:, :, :, 2]
        self.h_grid_min, self.h_grid_max, self.h_grid_n = \
            (np.amin(self.h_map), np.amax(self.h_map), 250)
        self.k_grid_min, self.k_grid_max, self.k_grid_n = \
            (np.amin(self.k_map), np.amax(self.k_map), 250)
        self.l_grid_min, self.l_grid_max, self.l_grid_n = \
            (np.amin(self.l_map), np.amax(self.l_map), 250)

    # TODO: Fix this absolute atrocity
    def setGriddingParameters(
        self,
        h_min, h_max, h_n,
        k_min, k_max, k_n,
        l_min, l_max, l_n
    ) -> None:
        """Sets HKL bounds and pixel counts for gridding."""

        self.h_grid_min, self.h_grid_max, self.h_grid_n = \
            (float(h_min), float(h_max), int(h_n))
        self.k_grid_min, self.k_grid_max, self.k_grid_n = \
            (float(k_min), float(k_max), int(k_n))
        self.l_grid_min, self.l_grid_max, self.l_grid_n = \
            (float(l_min), float(l_max), int(l_n))

    def gridImageData(self) -> None:
        """Creates a gridded array from raw image data and a RSM."""

        hkl_min = (self.h_grid_min, self.k_grid_min, self.l_grid_min)
        hkl_max = (self.h_grid_max, self.k_grid_max, self.l_grid_max)
        hkl_n = (self.h_grid_n, self.k_grid_n, self.l_grid_n)

        self.gridded_image_data, self.gridded_image_coords = gridScan(
            raw_image_data=self.raw_image_data,
            rsm=self.reciprocal_space_map,
            gridding_params=(hkl_min, hkl_max, hkl_n)
        )


class Curve:
    """Describes a 1-D line of values with coordinates and metadata."""

    ...
