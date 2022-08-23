"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import os

import numpy as np
from PIL import Image
from spec2nexus import spec

from imageanalysis.gridding import gridScan
from imageanalysis.mapping import mapScan


# TODO: Allow Pathlib paths
# TODO: Basic testing
class Project:
    """Houses SPEC/XML filepaths and Scans."""

    def __init__(
        self,
        project_path: str,
        spec_path: str,
        instrument_path: str,
        detector_path: str
    ) -> None:

        if project_path is None or type(project_path) != str:
            raise ValueError("Invalid project path.")
        if spec_path is None or type(spec_path) != str:
            raise ValueError("Invalid SPEC path.")
        if instrument_path is None or type(instrument_path) != str:
            raise ValueError("Invalid instrument configuration path.")
        if detector_path is None or type(detector_path) != str:
            raise ValueError("Invalid detector configuration path.")

        if not os.path.exists(project_path):
            raise NotADirectoryError(f"Path '{project_path}' not found.")
        if not os.path.exists(spec_path):
            raise FileNotFoundError(f"Path '{spec_path}' not found.")
        if not os.path.exists(instrument_path):
            raise FileNotFoundError(f"Path '{instrument_path}' not found.")
        if not os.path.exists(detector_path):
            raise FileNotFoundError(f"Path '{detector_path}' not found.")
        
        # Path variables
        self.path = project_path
        self.spec_path = spec_path
        self.instrument_path = instrument_path
        self.detector_path = detector_path

        # TODO: Check that image path exists
        spec_basename = os.path.basename(os.path.splitext(self.spec_path)[0])
        image_path = f"{project_path}/images/{spec_basename}"
        self.image_path = image_path

        # SPEC data object
        self.spec_data = spec.SpecDataFile(spec_path)

        # Create Scans
        self.scans = {}
        for n in self.getScanNumbers():
            scan = Scan(number=int(n), project=self)
            self.scans.update({int(n): scan})

    def getScanNumbers(self):
        """Returns list of scan numbers for project."""

        scan_numbers = []
        for n in self.spec_data.getScanNumbers():
            scan_image_path = self.image_path + f"/S{str(n).zfill(3)}"
            if os.path.exists(scan_image_path):
                scan_numbers.append(n)

        return scan_numbers

    def getScan(self, n):
        """Returns a Scan object for a given scan number"""
        return self.scans[n]


class Scan:
    """Houses data for a single scan."""

    def __init__(
        self,
        number: int,
        project: Project
    ) -> None:

        self.number = number
        self.project = project
        self.spec_scan = self.project.spec_data.getScan(number)
        self.raw_image_data, self.rsm = None, None
        self.gridded_image_data, self.gridded_image_coords = None, None
        self.grid_parameters = {
            "H": {"min": 0.0, "max": 0.0, "n": 250},
            "K": {"min": 0.0, "max": 0.0, "n": 250},
            "L": {"min": 0.0, "max": 0.0, "n": 250}
        }

    def _loadRawImageData(self) -> None:
        """Retrieves raw images."""

        scan_image_basepath = f"/S{str(self.number).zfill(3)}"
        scan_image_path = f"{self.project.image_path}/{scan_image_basepath}"
        image_paths = sorted(os.listdir(scan_image_path))
        image_paths = [
            p for p in image_paths if (
                not p.startswith(".") and
                not p.startswith("alignment") and
                p.endswith("tif")
            )
        ]

        # Normalization factors from SPEC
        monitor_norm_factors = self.spec_scan.data["Ion_Ch_2"] * 200000
        filter_norm_factors = self.spec_scan.data["transm"] * 1

        images = []
        # Retrieve image data from paths
        for i in range(len(image_paths)):
            img_path = f"{scan_image_path}/{image_paths[i]}"
            norm_factor = filter_norm_factors[i] * monitor_norm_factors[i]
            img = Image.open(img_path)
            img_array = np.array(img).T / norm_factor
            images.append(img_array)

        self.raw_image_data = np.array(images)

    def _mapRawImageData(self) -> None:
        """Creates a reciprocal space map from given parameters"""

        self.rsm = mapScan(
            spec_scan=self.spec_scan,
            instrument_path=self.project.instrument_path,
            detector_path=self.project.detector_path
        )
        self._resetGridParameters()

    def _gridRawImageData(self) -> None:
        """Creates a gridded array from raw image data and a RSM."""

        self.gridded_image_data, self.gridded_image_coords = gridScan(
            raw_image_data=self.raw_image_data,
            rsm=self.rsm,
            grid_params=self.grid_parameters
        )

    def _setGridParameters(self, params: dict) -> None:
        """Sets parameters for gridding."""

        self.grid_parameters["H"]["min"] = params["H"]["min"]
        self.grid_parameters["K"]["min"] = params["K"]["min"]
        self.grid_parameters["L"]["min"] = params["L"]["min"]
        self.grid_parameters["H"]["max"] = params["H"]["max"]
        self.grid_parameters["K"]["max"] = params["K"]["max"]
        self.grid_parameters["L"]["max"] = params["L"]["max"]
        self.grid_parameters["H"]["n"] = params["H"]["n"]
        self.grid_parameters["K"]["n"] = params["K"]["n"]
        self.grid_parameters["L"]["n"] = params["L"]["n"]

    def _resetGridParameters(self) -> None:
        """Resets gridding parameters to defaults."""

        self.grid_parameters["H"]["min"] = np.amin(self.rsm[:, :, :, 0])
        self.grid_parameters["K"]["min"] = np.amin(self.rsm[:, :, :, 1])
        self.grid_parameters["L"]["min"] = np.amin(self.rsm[:, :, :, 2])
        self.grid_parameters["H"]["max"] = np.amax(self.rsm[:, :, :, 0])
        self.grid_parameters["K"]["max"] = np.amax(self.rsm[:, :, :, 1])
        self.grid_parameters["L"]["max"] = np.amax(self.rsm[:, :, :, 2])
        self.grid_parameters["H"]["n"] = 250
        self.grid_parameters["K"]["n"] = 250
        self.grid_parameters["L"]["n"] = 250


class Curve:
    """Describes a 1-D line of values with coordinates and metadata."""

    ...
