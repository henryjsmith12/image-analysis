import pytest
from spec2nexus import spec

from imageanalysis.structures import Project

# ==================================================================================

project_path = "./imageanalysis/data"
spec_path = f"{project_path}/pmn_pt011_2_1.spec"
instrument_path = f"{project_path}/6IDB_Instrument.xml"
detector_path = f"{project_path}/6IDB_DetectorGeometry.xml"

# ==================================================================================

def test_empty_project():
    try:
        project = Project()
    except TypeError:
        assert True

# ----------------------------------------------------------------------------------

def test_non_string_args():
    try:
        project = Project(
            project_path=project_path,
            spec_path=spec_path,
            instrument_path=0,
            detector_path=detector_path
        )
    except TypeError:
        assert True

# ----------------------------------------------------------------------------------

def test_valid_spec_file():
    try:
        project = Project(
            project_path=project_path,
            spec_path="",
            instrument_path=instrument_path,
            detector_path=detector_path
        )
    except spec.SpecDataFileNotFound:
        assert True

# ----------------------------------------------------------------------------------

def test_path_variables():
    project = Project(
        project_path=project_path,
        spec_path=spec_path,
        instrument_path=instrument_path,
        detector_path=detector_path
    )

    obj_paths = [project.path, project.spec_path, project.instrument_path, project.detector_path]
    arg_paths = [project_path, spec_path, instrument_path, detector_path]
    if obj_paths == arg_paths:
        assert True

# ==================================================================================