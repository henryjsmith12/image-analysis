"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import os
from xml.etree import ElementTree

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
    Returns a list of SPEC files immediately below given directory.
    """

    spec_paths = []

    for item in os.listdir(path):
        item_path = f"{path}/{item}"
        if item.endswith(".spec"):
            spec_paths.append(item_path)

    return spec_paths

# ==================================================================================

def getXMLPaths(path):
    """
    Returns a list of XML files immediately below given directory.
    """

    xml_paths = []

    for item in os.listdir(path):
        item_path = f"{path}/{item}"
        if item.endswith(".xml"):
            xml_paths.append(item_path)

    return xml_paths

# ==================================================================================

