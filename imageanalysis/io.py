"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
import os
import vtk
from vtk.util import numpy_support

from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import \
    DetectorGeometryForXrayutilitiesReader  # isValidDetectorXMLFile
from rsMap3D.datasource.InstForXrayutilitiesReader import \
    InstForXrayutilitiesReader  # isValidInstrumentXMLFile
from spec2nexus import spec  # isValidSPECFile


# TODO: Basic testing for all functions
# TODO: Pathlib capabilities
def isValidProjectPath(path: str) -> bool:
    """Checks if path is a valid Project path.

    A valid project directory includes: A SPEC file (.spec), instrument and
    detector configuration files (.xml), and an "images" subdirectory.
    """

    # Hold status of each required element
    spec, instr_config, det_config, images = False, False, False, False

    # Evaluates every item in given directory path until conditions are met
    for item in os.listdir(path):

        item_path = f"{path}/{item}"

        # Checks if item is a directory
        if os.path.isdir(item_path):
            # "images" subdirectory
            if item == "images":
                images = True

        # Checks if item is a file
        elif os.path.isfile(item_path):
            # SPEC file
            if item.endswith(".spec"):
                    spec = True
            # Configuration files
            elif item.endswith(".xml"):
                if isValidInstrumentXMLFile(item_path):
                    instr_config = True
                elif isValidDetectorXMLFile(item_path):
                    det_config = True

        # Checks if conditions for Project path are met
        is_valid = False not in [spec, instr_config, det_config, images]
        if is_valid:
            break

    return is_valid


def isValidSPECFile(path: str) -> bool:
    """Checks if given path is a valid SPEC file."""

    try:
        # Pip package version: Always returns as False on first runthrough
        # Second try/except block added to catch this oddity.
        # I have no idea why only the package version has this error.
        spec_data = spec.SpecDataFile(path)
        return True
    except:
        try:
            spec_data = spec.SpecDataFile(path)
            return True
        except:
            return False


def isValidInstrumentXMLFile(path: str) -> bool:
    """Checks if given path is a valid instrument configuration file."""

    try:
        instrument_reader = InstForXrayutilitiesReader(path)
        # Raises an error if getSampleCircleDirections() is empty
        sc = instrument_reader.getSampleCircleDirections()
    except:
        return False

    return True


def isValidDetectorXMLFile(path: str) -> bool:
    """Checks if given path is a valid detector configuration file."""

    try:
        detector_reader = DetectorGeometryForXrayutilitiesReader(path)
        # Raises an error if getDetectors() is empty
        detector = detector_reader.getDetectors()[0]
    except:
        return False

    return True


def getSPECPaths(path: str) -> list:
    """Returns list of SPEC file basepaths in given directory."""

    spec_paths = []

    for item in os.listdir(path):
        if item.endswith(".spec"):
            spec_paths.append(item)

    return spec_paths


def getXMLPaths(path: str) -> list:
    """Returns list of XML file basepaths in given directory."""

    xml_paths = []

    for item in os.listdir(path):
        if item.endswith(".xml"):
            xml_paths.append(item)

    return xml_paths


def numpyToVTK(array: np.ndarray, coords, path) -> str:
    """Converts and saves numpy array to VTK image data."""

    data_array = numpy_support.numpy_to_vtk(array.flatten(order="F"))
    image_data = vtk.vtkImageData()

    qx_0, qy_0, qz_0 = coords[0][0], coords[1][0], coords[2][0]
    del_qx = coords[0][1] - coords[0][0]
    del_qy = coords[1][1] - coords[1][0]
    del_qz = coords[2][1] - coords[2][0]

    image_data.SetOrigin(qx_0, qy_0, qz_0)
    image_data.SetSpacing(del_qx, del_qy, del_qz)
    image_data.SetDimensions(*array.shape)

    image_data.GetPointData().SetScalars(data_array)

    writer = vtk.vtkXMLImageDataWriter()
    writer.SetFileName(path)
    writer.SetInputData(image_data)
    writer.Write()
