"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import os

from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import \
    DetectorGeometryForXrayutilitiesReader  # isValidDetectorXMLFile
from rsMap3D.datasource.InstForXrayutilitiesReader import \
    InstForXrayutilitiesReader  # isValidInstrumentXMLFile
from spec2nexus import spec  # isValidSPECFile


# TODO: Basic testing for all functions

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

            # At least 2 configuration files
            # Configuration files are validated when Project object is created
            elif item.endswith(".xml"):
                if not instr_config:
                    instr_config = True
                else:
                    det_config = True

        # Checks if conditions for Project path are met
        is_valid = False not in [spec, instr_config, det_config, images]
        if is_valid:
            break

    return is_valid


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


def isValidSPECFile(path: str) -> bool:
    """Checks if given path is a valid SPEC file."""

    try:
        spec_data = spec.SpecDataFile(path)
        return True
    except:
        return False


def isValidInstrumentXMLFile(path: str) -> bool:
    """Checks if given path is a valid instrument configuration file."""

    try:
        instrument_reader = InstForXrayutilitiesReader(path)
        sc = instrument_reader.getSampleCircleDirections()
    except:
        return False

    return True


def isValidDetectorXMLFile(path: str) -> bool:
    """Checks if given path is a valid detector configuration file."""

    try:
        detector_reader = DetectorGeometryForXrayutilitiesReader(path)
        detector = detector_reader.getDetectors()[0]
    except:
        return False

    return True
