"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import os
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import DetectorGeometryForXrayutilitiesReader
from rsMap3D.datasource.InstForXrayutilitiesReader import InstForXrayutilitiesReader
from spec2nexus import spec

# ==================================================================================

def isValidProjectPath(path):
    """
    Check if a path has the correct structure to be a project path. A valid project 
    directory includes: A SPEC file (.spec), instrument and detector configuration 
    files (.xml), and an "images" subdirectory.
    """

    spec, instr_config, det_config, images = False, False, False, False

    for item in os.listdir(path):
        item_path = f"{path}/{item}"
        if os.path.isdir(item_path):
            if item == "images":
                images = True
        elif os.path.isfile(item_path):
            if item.endswith(".spec"):
                spec = True
            elif item.endswith(".xml"):
                if not instr_config:
                    instr_config = True
                else:
                    det_config = True
        is_valid = not False in [spec, instr_config, det_config, images]
        if is_valid:
            break

    return is_valid
    
# ==================================================================================

def getSPECPaths(path):
    """
    Returns a list of SPEC file basepaths immediately below given directory.
    """

    spec_paths = []

    for item in os.listdir(path):
        if item.endswith(".spec"):
            spec_paths.append(item)

    return spec_paths

# ==================================================================================

def getXMLPaths(path):
    """
    Returns a list of XML file basepaths immediately below given directory.
    """

    xml_paths = []

    for item in os.listdir(path):
        if item.endswith(".xml"):
            xml_paths.append(item)

    return xml_paths

# ==================================================================================

def isValidSPECFile(path):
    try:
        spec_data = spec.SpecDataFile(path)
        return True
    except:
        return False

# ==================================================================================

def isValidInstrumentXMLFile(path):
    try:
        instrument_reader = InstForXrayutilitiesReader(path)
        sc = instrument_reader.getSampleCircleDirections()
    except:
        return False

    return True

# ==================================================================================

def isValidDetectorXMLFile(path):
    try:
        detector_reader = DetectorGeometryForXrayutilitiesReader(path)
        detector = detector_reader.getDetectors()[0]
    except:
        return False

    return True


# ==================================================================================

