"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import \
    DetectorGeometryForXrayutilitiesReader
from rsMap3D.datasource.InstForXrayutilitiesReader import \
    InstForXrayutilitiesReader
from spec2nexus import spec
import xrayutilities as xu


# TODO: Make arbitrary enough to use as a static function
def mapScan(
    spec_scan: spec.SpecDataFileScan,
    instrument_path: str,
    detector_path: str
) -> np.ndarray:
    """Creates a reciprocal space map for each point in a scan."""

    point_rsm_list = []
    angle_names = []
    rsm_params = {"Energy": 0, "UB_Matrix": None}

    # rsMap3D XML readers
    instrument_reader = InstForXrayutilitiesReader(instrument_path)
    detector_reader = DetectorGeometryForXrayutilitiesReader(detector_path)

    # Names of angles used in instrument geometry
    # xrayutilities expects sample circles then detector circles
    sample_circle_names = instrument_reader.getSampleCircleNames()
    detector_circle_names = instrument_reader.getDetectorCircleNames()
    angle_names = sample_circle_names + detector_circle_names

    # Adds each angle to RSM parameters dictionary
    for angle in angle_names:
        rsm_params.update({angle: 0})

    # Checks for initial values of all RSM parameters in spec header
    # Updates parameter if found
    for param in rsm_params.keys():
        if param in spec_scan.positioner:
            rsm_params[param] = spec_scan.positioner[param]

    # Retrieves UB matrix
    ub_list = spec_scan.G["G3"].split(" ")

    # Adds UB matrix to parameters as a 3x3 array
    rsm_params["UB_Matrix"] = np.reshape(ub_list, (3, 3)).astype(np.float64)

    # Retrieves initial energy value
    # Hard-coded because this appears to be user-supplied
    for line in spec_scan.raw.split("\n"):
        if line.startswith("#U"):

            # Updates Energy parameter
            # Converted to eV from keV
            rsm_params["Energy"] = float(line.split(" ")[1]) * 1000
            break

    # Retrieve total number of scan points from spec
    point_count = len(spec_scan.data_lines)

    # Creates a reciprocal space map for every scan point
    for i in range(point_count):
        point_rsm = mapScanPoint(
            point=i,
            spec_scan=spec_scan,
            rsm_params=rsm_params,
            angle_names=angle_names,
            instrument_reader=instrument_reader,
            detector_reader=detector_reader
        )
        point_rsm_list.append(point_rsm)

    # Convert RSM list to 3D array
    rsm = np.array(point_rsm_list)
    rsm = rsm.swapaxes(1, 3)
    rsm = rsm.swapaxes(1, 2)

    return rsm


def mapScanPoint(
    point: int,
    spec_scan: spec.SpecDataFileScan,
    rsm_params: dict,
    angle_names: list,
    instrument_reader: InstForXrayutilitiesReader,
    detector_reader: DetectorGeometryForXrayutilitiesReader
) -> np.ndarray:
    """Creates a reciprocal space map for a single scan point."""

    # Gathers parameter values from SPEC data columns
    for i in range(len(spec_scan.L)):
        label = spec_scan.L[i]
        if label in rsm_params.keys():
            rsm_params[label] = spec_scan.data[label][point]

    # RSM process
    # See xrayutilities documentation for more info
    sample_circle_dir = instrument_reader.getSampleCircleDirections()
    det_circle_dir = instrument_reader.getDetectorCircleDirections()
    primary_beam_dir = instrument_reader.getPrimaryBeamDirection()
    q_conv = xu.experiment.QConversion(
        sample_circle_dir,
        det_circle_dir,
        primary_beam_dir
    )
    inplane_ref_dir = instrument_reader.getInplaneReferenceDirection()
    sample_norm_dir = instrument_reader.getSampleSurfaceNormalDirection()
    hxrd = xu.HXRD(
        inplane_ref_dir,
        sample_norm_dir,
        en=rsm_params["Energy"],
        qconv=q_conv
    )
    detector = detector_reader.getDetectors()[0]
    pixel_dir_1 = detector_reader.getPixelDirection1(detector)
    pixel_dir_2 = detector_reader.getPixelDirection2(detector)
    c_ch_1 = detector_reader.getCenterChannelPixel(detector)[0]
    c_ch_2 = detector_reader.getCenterChannelPixel(detector)[1]
    n_ch_1 = detector_reader.getNpixels(detector)[0]
    n_ch_2 = detector_reader.getNpixels(detector)[1]
    pixel_width_1 = detector_reader.getSize(detector)[0] / n_ch_1
    pixel_width_2 = detector_reader.getSize(detector)[1] / n_ch_2
    distance = detector_reader.getDistance(detector)
    roi = [0, n_ch_1, 0, n_ch_2]
    hxrd.Ang2Q.init_area(
        pixel_dir_1, pixel_dir_2,
        cch1=c_ch_1, cch2=c_ch_2,
        Nch1=n_ch_1, Nch2=n_ch_2,
        pwidth1=pixel_width_1, pwidth2=pixel_width_2,
        distance=distance, roi=roi
    )

    # Retrieves angle values from parameter dictionary
    angle_values = [rsm_params[angle] for angle in angle_names]
    qx, qy, qz = hxrd.Ang2Q.area(*angle_values, UB=rsm_params["UB_Matrix"])

    # Converts list to array
    point_rsm = np.array([qx, qy, qz])

    return point_rsm
