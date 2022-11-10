import pytest

from imageanalysis.structures import Project

def test_project_creation_success():
    p = Project(
        project_path="sample_project/",
        spec_path="sample_project/pmn_pt011_2_1.spec",
        instrument_path="sample_project/6IDB_Instrument.xml",
        detector_path="sample_project/6IDB_DetectorGeometry.xml"
    )


def test_project_creation_empty_project_path():
    with pytest.raises(ValueError) as ex_info:
        p = Project(
            project_path=None,
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_empty_spec_path():
    with pytest.raises(ValueError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path=None,
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_empty_instrument_path():
    with pytest.raises(ValueError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path=None,
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_empty_detector_path():
    with pytest.raises(ValueError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path=None
        )

def test_project_creation_nonstring_project_path():
    with pytest.raises(ValueError) as ex_info:
        p = Project(
            project_path=42,
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_nonstring_spec_path():
    with pytest.raises(ValueError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path=42,
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_nonstring_instrument_path():
    with pytest.raises(ValueError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path=42,
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_nonstring_detector_path():
    with pytest.raises(ValueError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path=42
        )

def test_project_creation_nonstring_project_path():
    with pytest.raises(NotADirectoryError) as ex_info:
        p = Project(
            project_path="INVALID_PATH_STRING",
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_nonstring_spec_path():
    with pytest.raises(FileNotFoundError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path="INVALID_PATH_STRING",
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_nonstring_instrument_path():
    with pytest.raises(FileNotFoundError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path="INVALID_PATH_STRING",
            detector_path="sample_project/6IDB_DetectorGeometry.xml"
        )


def test_project_creation_nonstring_detector_path():
    with pytest.raises(FileNotFoundError) as ex_info:
        p = Project(
            project_path="sample_project/",
            spec_path="sample_project/pmn_pt011_2_1.spec",
            instrument_path="sample_project/6IDB_Instrument.xml",
            detector_path="INVALID_PATH_STRING"
        )
