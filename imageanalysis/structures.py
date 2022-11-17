"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
import os
from PIL import Image
from spec2nexus import spec

from imageanalysis.gridding import gridScan
from imageanalysis.mapping import mapScan


class Project:
    """General object that handles SPEC data and configuration files."""

    path = None # Absolute project path
    spec_path = None # SPEC data file
    detector_path = None # Detector config XML
    instrument_path = None # Instrument config XML
    image_path = None # Raw image directory
    name = None # Visible project name
    spec_data = None # spec2nexus.SpecDataFile for project
    scans = None # Dict of Scan objects for project

    def __init__(
        self,
        project_path: str,
        spec_path: str,
        instrument_path: str,
        detector_path: str
    ) -> None:

        # Parameters
        self._validateParameters(
            project_path, 
            spec_path, 
            instrument_path, 
            detector_path
        )
        self.path = project_path
        self.spec_path = spec_path
        self.instrument_path = instrument_path
        self.detector_path = detector_path

        # Image path
        image_path = self._getImagePath(project_path, spec_path)
        self._validateImagePath(image_path)
        self.image_path = image_path

        # Name
        self.name = os.path.basename(image_path)

        # Creates SpecDataFile based on SPEC file contents
        self.spec_data = spec.SpecDataFile(spec_path)

        # Creates Scans
        self._createScans()

    def _validateParameters(
        self,
        project_path: str,
        spec_path: str,
        instrument_path: str,
        detector_path: str
    ) -> None:
        """Basic validation for Project arguments."""

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

    def _getImagePath(
        self, 
        project_path: str, 
        spec_path: str
    ) -> str:
        """Checks if image path directory is present in project path."""

        spec_basename = os.path.basename(spec_path)
        spec_basename_without_ext = os.path.splitext(spec_basename)[0]
        image_path = f"{project_path}/images/{spec_basename_without_ext}"
        
        if os.path.exists(image_path):
            return image_path
        else:
            return None

    def _validateImagePath(
        self, 
        image_path: str
    ) -> None:
        """Basic validation for image path directory"""

        if image_path is None:
            raise NotADirectoryError(f"Path '{image_path}' not found.")

    def _createScans(self) -> None:
        """Creates a dict of Scan objects created from SPEC and image data."""

        scans = {}

        for n in self.spec_data.getScanNumbers():
            scan_image_path = self.image_path + f"/S{str(n).zfill(3)}"
            spec_scan = self.spec_data.getScan(n)

            if os.path.exists(scan_image_path):
                scan = Scan(
                    project=self,
                    image_path=scan_image_path,
                    spec_scan=spec_scan
                )
                scans.update({int(n): scan})

        self.scans = scans

class Scan:
    """Houses data for a scan."""

    project = None # Parent project
    image_path = None # Directory with raw images for scan
    spec_scan = None # SpecDataFileScan
    number = None # Number assigned in SPEC data
    name = None # Visible name for scan
    raw_data = None # 3D NumPy array for raw image data
    rsm = None # 4D NumPy array with reciprocal space map
    grid_data = None # 3D NumPy array for gridded image data
    grid_coords = None # 2D list of gridded coordinates for HKL, respectively
    grid_params = None # Parameters for gridding raw image data
    
    def __init__(
        self,
        project: Project,
        image_path: str,
        spec_scan: spec.SpecDataFileScan
    ) -> None:
        
        self.project = project
        self.image_path = image_path
        self.spec_scan = spec_scan
        self.number = spec_scan.scanNum
        self.name = f"{self.number} ({project.name})"
        self.grid_params = {
            "H": {"min": 0.0, "max": 0.0, "n": 250},
            "K": {"min": 0.0, "max": 0.0, "n": 250},
            "L": {"min": 0.0, "max": 0.0, "n": 250}
        }

    def loadRawData(self) -> None:
        """Loads raw images from image path directory."""

        # Determines image files to read
        image_files = []
        for file in sorted(os.listdir(self.image_path)):
            if self.project.name in file and file.endswith("tif"):
                image_files.append(file)

        # Reads and normalizes images
        raw_images = []
        for i in range(len(image_files)): 
            basepath = image_files[i]
            path = f"{self.image_path}/{basepath}"
            image = self._readImageFromPath(path)
            norm_image = self._normalizeRawImage(image, point=i)
            raw_images.append(norm_image)

        self.raw_data = np.array(raw_images)

    def map(self) -> None:
        """Creates a reciprocal space map."""

        self.rsm = mapScan(
            spec_scan=self.spec_scan,
            instrument_path=self.project.instrument_path,
            detector_path=self.project.detector_path
        )

    def setGridSize(
        self, 
        h_n: int, 
        k_n: int, 
        l_n: int
    ) -> None:
        """Sets pixel count for each dimension of gridded data."""
        
        self.grid_params["H"]["n"] = h_n
        self.grid_params["K"]["n"] = k_n
        self.grid_params["L"]["n"] = l_n

    def setGridBounds(
        self,
        h_min: float, h_max: float,
        k_min: float, k_max: float,
        l_min: float, l_max: float
    ) -> None:
        """Sets bounds for each dimension of gridded data."""
        
        self.grid_params["H"]["min"] = h_min
        self.grid_params["K"]["min"] = k_min
        self.grid_params["L"]["min"] = l_min
        self.grid_params["H"]["max"] = h_max
        self.grid_params["K"]["max"] = k_max
        self.grid_params["L"]["max"] = l_max

    def grid(self) -> None:
        """Creates a 3D reconstruction of the raw data using a RSM."""

        # Grids raw image data
        self.grid_data, self.grid_coords = gridScan(
            raw_image_data=self.raw_data,
            rsm=self.rsm,
            grid_params=self.grid_params
        )
    
    def _readImageFromPath(
        self, 
        image_path: str
    ) -> np.ndarray:
        """Reads image from given path."""

        image = Image.open(image_path)
        image_array = np.array(image).T

        return image_array

    def _normalizeRawImage(
        self, 
        image: np.ndarray, 
        point: int
    ) -> np.ndarray:
        """Normalizes raw image with SPEC values."""

        monitor_norm_factor = self.spec_scan.data["Ion_Ch_2"][point] / 200000
        filter_norm_factor = self.spec_scan.data["transm"][point]
        norm_factor = monitor_norm_factor * filter_norm_factor
        norm_image = image * norm_factor

        return norm_image

    def _setDefaultGridParameters(self) -> None:
        """Changes grid parameters to default bounds and size.
        
        - Default bounds are the min/max bounds of current RSM
        - Default size is (250, 250, 250)
        """
        h = self.rsm[:, :, :, 0]
        k = self.rsm[:, :, :, 1]
        l = self.rsm[:, :, :, 2]

        h_min, h_max = np.amin(h), np.amax(h)
        k_min, k_max = np.amin(k), np.amax(k)
        l_min, l_max = np.amin(l), np.amax(l)
        
        self.grid_params = {
            "H": {"min": h_min, "max": h_max, "n": 250},
            "K": {"min": k_min, "max": k_max, "n": 250},
            "L": {"min": l_min, "max": l_max, "n": 250}
        }


class Curve:
    """Describes a 1-D line of values with coordinates and metadata."""

    def __init__(
        self, 
        data: np.ndarray, 
        labels: list, 
        coords: list, 
        metadata: dict=None
    ) -> None:

        self.data = data
        self.labels = labels
        self.coords = coords
        self.metadata = metadata