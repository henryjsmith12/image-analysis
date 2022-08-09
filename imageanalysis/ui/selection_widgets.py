"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
from pyqtgraph import QtGui

from imageanalysis.io import \
    isValidProjectPath, getSPECPaths, getXMLPaths
from imageanalysis.structures import Project


class ProjectSelectionWidget(QtGui.QWidget):
    """Handles project and project-dependent file selection."""

    def __init__(self, parent) -> None:
        super(ProjectSelectionWidget, self).__init__()

        self.main_window = parent

        # Path variables
        self.project_path = None
        self.spec_path = None
        self.instrument_path = None
        self.detector_path = None

        # Child widgets
        self.project_btn = QtGui.QPushButton("Select Project")
        self.project_txt = QtGui.QLineEdit()
        self.project_txt.setReadOnly(True)
        self.project_files_gbx = QtGui.QGroupBox()
        self.project_files_gbx.setEnabled(False)
        self.spec_lbl = QtGui.QLabel("SPEC Source:")
        self.spec_cbx = QtGui.QComboBox()
        self.instrument_lbl = QtGui.QLabel("Instrument:")
        self.instrument_cbx = QtGui.QComboBox()
        self.detector_lbl = QtGui.QLabel("Detector:")
        self.detector_cbx = QtGui.QComboBox()
        self.load_project_btn = QtGui.QPushButton("Load Project")
        self.load_project_btn.setEnabled(False)

        # Project files GroupBox layout
        self.project_files_gbx_layout = QtGui.QGridLayout()
        self.project_files_gbx.setLayout(self.project_files_gbx_layout)
        self.project_files_gbx_layout.addWidget(self.spec_lbl, 0, 0)
        self.project_files_gbx_layout.addWidget(self.spec_cbx, 0, 1)
        self.project_files_gbx_layout.addWidget(self.instrument_lbl, 1, 0)
        self.project_files_gbx_layout.addWidget(self.instrument_cbx, 1, 1)
        self.project_files_gbx_layout.addWidget(self.detector_lbl, 2, 0)
        self.project_files_gbx_layout.addWidget(self.detector_cbx, 2, 1)
        self.project_files_gbx_layout.addWidget(self.load_project_btn, 3, 1)

        # Main layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.project_btn, 0, 0)
        self.layout.addWidget(self.project_txt, 0, 1)
        self.layout.addWidget(self.project_files_gbx, 1, 0, 1, 2)

        # Connections
        self.project_btn.clicked.connect(self.selectProject)
        self.spec_cbx.currentTextChanged.connect(
            self.enableLoadProjectButton
        )
        self.instrument_cbx.currentTextChanged.connect(
            self.enableLoadProjectButton
        )
        self.detector_cbx.currentTextChanged.connect(
            self.enableLoadProjectButton
        )
        self.load_project_btn.clicked.connect(self.loadProject)

    def selectProject(self) -> None:
        """Allows user to select a project directory."""

        project_path = QtGui.QFileDialog.getExistingDirectory(
            self, "Select Project"
        )

        # Checks if project path is valid
        if isValidProjectPath(project_path):
            self.project_path = project_path
            self.project_txt.setText(project_path)
            self.project_files_gbx.setEnabled(True)
            self.populateProjectFilesGroupbox()
        else:
            self.project_files_gbx.setEnabled(False)
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Invalid project directory.")
            msg.exec_()

    def populateProjectFilesGroupbox(self) -> None:
        """Adds SPEC files and XML files to comboboxes."""

        self.spec_cbx.clear()
        self.instrument_cbx.clear()
        self.detector_cbx.clear()

        spec_paths = getSPECPaths(self.project_path)
        xml_paths = getXMLPaths(self.project_path)

        self.spec_cbx.addItems(spec_paths)
        self.instrument_cbx.addItems(xml_paths)
        self.detector_cbx.addItems(xml_paths)

    def enableLoadProjectButton(self) -> None:
        """Enables "Load Project" button."""

        self.spec_path = f"{self.project_path}/" \
            f"{self.spec_cbx.currentText()}"
        self.instrument_path = f"{self.project_path}/" \
            f"{self.instrument_cbx.currentText()}"
        self.detector_path = f"{self.project_path}/" \
            f"{self.detector_cbx.currentText()}"

        self.load_project_btn.setEnabled(True)

    def loadProject(self) -> None:
        """Creates and loads Project object."""

        # Attempts to create and load Project with given file paths
        try:
            self.project = Project(
                project_path=self.project_path,
                spec_path=self.spec_path,
                instrument_path=self.instrument_path,
                detector_path=self.detector_path
            )
            # Loads project scans
            self.main_window.scan_selection_widget.loadProjectScanList(
                self.project
            )
        except Exception as ex:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(ex.args[-1])
            msg.exec_()


class ScanSelectionWidget(QtGui.QWidget):
    """Handles scan selection and loading."""

    def __init__(self, parent) -> None:
        super(ScanSelectionWidget, self).__init__()

        self.main_window = parent

        # Project
        self.project = None

        # Scans that have been previewed
        self.previewed_scans = []

        # Child widgets
        self.scan_lstw = QtGui.QListWidget()
        self.scan_details_gbx = QtGui.QGroupBox()
        self.scan_details_gbx.setEnabled(False)
        self.scan_number_lbl = QtGui.QLabel("Scan:")
        self.scan_number_txt = QtGui.QLineEdit()
        self.scan_number_txt.setReadOnly(True)
        self.scan_point_count_lbl = QtGui.QLabel("# Points:")
        self.scan_point_count_txt = QtGui.QLineEdit()
        self.scan_point_count_txt.setReadOnly(True)
        self.scan_date_lbl = QtGui.QLabel()
        self.scan_type_lbl = QtGui.QLabel()
        self.scan_bounds_lbl = QtGui.QLabel()
        self.gridding_options_gbx = QtGui.QGroupBox()
        self.gridding_options_gbx.setTitle("Gridding Options")
        self.min_lbl = QtGui.QLabel("Min")
        self.max_lbl = QtGui.QLabel("Max")
        self.n_lbl = QtGui.QLabel("n")
        self.h_lbl = QtGui.QLabel("H:")
        self.h_min_sbx = QtGui.QDoubleSpinBox()
        self.h_max_sbx = QtGui.QDoubleSpinBox()
        self.h_n_sbx = QtGui.QSpinBox()
        self.k_lbl = QtGui.QLabel("K:")
        self.k_min_sbx = QtGui.QDoubleSpinBox()
        self.k_max_sbx = QtGui.QDoubleSpinBox()
        self.k_n_sbx = QtGui.QSpinBox()
        self.l_lbl = QtGui.QLabel("L:")
        self.l_min_sbx = QtGui.QDoubleSpinBox()
        self.l_max_sbx = QtGui.QDoubleSpinBox()
        self.l_n_sbx = QtGui.QSpinBox()
        self.reset_btn = QtGui.QPushButton("Reset")
        self.load_scan_btn = QtGui.QPushButton("Load Scan")

        # SpinBox properties
        for sbx in [
            self.h_min_sbx, self.h_max_sbx,
            self.k_min_sbx, self.k_max_sbx,
            self.l_min_sbx, self.l_max_sbx
        ]:
            sbx.setDecimals(3)
            sbx.setRange(-100, 100)
            sbx.setSingleStep(0.001)
        for sbx in [self.h_n_sbx, self.k_n_sbx, self.l_n_sbx]:
            sbx.setRange(1, 1000)

        # Scan details GroupBox layout
        self.scan_details_gbx_layout = QtGui.QGridLayout()
        self.scan_details_gbx.setLayout(self.scan_details_gbx_layout)
        self.scan_details_gbx_layout.addWidget(
            self.scan_number_lbl, 0, 0)
        self.scan_details_gbx_layout.addWidget(
            self.scan_number_txt, 0, 1)
        self.scan_details_gbx_layout.addWidget(
            self.scan_point_count_lbl, 0, 2)
        self.scan_details_gbx_layout.addWidget(
            self.scan_point_count_txt, 0, 3)
        self.scan_details_gbx_layout.addWidget(
            self.scan_date_lbl, 1, 0, 1, 4)
        self.scan_details_gbx_layout.addWidget(
            self.scan_type_lbl, 2, 0)
        self.scan_details_gbx_layout.addWidget(
            self.scan_bounds_lbl, 2, 1, 1, 3)
        self.scan_details_gbx_layout.addWidget(
            self.gridding_options_gbx, 3, 0, 1, 4)
        self.scan_details_gbx_layout.addWidget(
            self.load_scan_btn, 4, 2, 1, 2)

        # gridding options GroupBox layout
        self.gridding_options_gbx_layout = QtGui.QGridLayout()
        self.gridding_options_gbx.setLayout(self.gridding_options_gbx_layout)
        self.gridding_options_gbx_layout.addWidget(self.min_lbl, 0, 1)
        self.gridding_options_gbx_layout.addWidget(self.max_lbl, 0, 2)
        self.gridding_options_gbx_layout.addWidget(self.n_lbl, 0, 3)
        self.gridding_options_gbx_layout.addWidget(self.h_lbl, 1, 0)
        self.gridding_options_gbx_layout.addWidget(self.h_min_sbx, 1, 1)
        self.gridding_options_gbx_layout.addWidget(self.h_max_sbx, 1, 2)
        self.gridding_options_gbx_layout.addWidget(self.h_n_sbx, 1, 3)
        self.gridding_options_gbx_layout.addWidget(self.k_lbl, 2, 0)
        self.gridding_options_gbx_layout.addWidget(self.k_min_sbx, 2, 1)
        self.gridding_options_gbx_layout.addWidget(self.k_max_sbx, 2, 2)
        self.gridding_options_gbx_layout.addWidget(self.k_n_sbx, 2, 3)
        self.gridding_options_gbx_layout.addWidget(self.l_lbl, 3, 0)
        self.gridding_options_gbx_layout.addWidget(self.l_min_sbx, 3, 1)
        self.gridding_options_gbx_layout.addWidget(self.l_max_sbx, 3, 2)
        self.gridding_options_gbx_layout.addWidget(self.l_n_sbx, 3, 3)
        self.gridding_options_gbx_layout.addWidget(self.reset_btn, 4, 0, 1, 4)

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.scan_lstw, 0, 0)
        self.layout.addWidget(self.scan_details_gbx, 1, 0)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 2)

        # Connections
        self.scan_lstw.itemClicked.connect(self.previewScan)
        self.reset_btn.clicked.connect(self.resetGriddingOptions)
        self.load_scan_btn.clicked.connect(self.loadScan)

    def loadProjectScanList(self, project) -> None:
        """Populates scan list."""

        self.project = project
        self.scan_lstw.clear()
        self.scan_lstw.addItems(self.project.scan_numbers)

    def clearProjectScanList(self) -> None:
        """Clears scan list."""

        self.scan_lstw.clear()

    def previewScan(self) -> None:
        """Displays preview information for currently selected scan."""

        # Retrieve current scan
        i = self.scan_lstw.currentRow()
        scan = self.project.scans[i]

        # Loads RSM and raw image data if not previously previewed
        if scan not in self.previewed_scans:
            self.project.scans[i].raw_image_data = scan.getImageData()
            self.project.scans[i].mapImageData()
            self.previewed_scans.append(scan)

        # Scan header details from SPEC
        header = scan.spec_scan.S.split()
        number = header[0]
        type = f"{header[1]} {header[2]}"
        bounds = f"({header[3]}, {header[4]})"
        point_count = str(len(scan.spec_scan.data_lines))
        date = scan.spec_scan.date

        # Displays scan details in child widgets
        self.scan_number_txt.setText(number)
        self.scan_point_count_txt.setText(point_count)
        self.scan_date_lbl.setText(date)
        self.scan_type_lbl.setText(type)
        self.scan_bounds_lbl.setText(bounds)
        self.h_min_sbx.setValue(round(scan.h_grid_min, 3))
        self.h_max_sbx.setValue(round(scan.h_grid_max, 3))
        self.h_n_sbx.setValue(scan.h_grid_n)
        self.k_min_sbx.setValue(round(scan.k_grid_min, 3))
        self.k_max_sbx.setValue(round(scan.k_grid_max, 3))
        self.k_n_sbx.setValue(scan.k_grid_n)
        self.l_min_sbx.setValue(round(scan.l_grid_min, 3))
        self.l_max_sbx.setValue(round(scan.l_grid_max, 3))
        self.l_n_sbx.setValue(scan.l_grid_n)

        self.scan_details_gbx.setEnabled(True)

    def resetGriddingOptions(self) -> None:
        """Resets gridding parameters to default values for scan."""

        # Retrieves current scan
        i = self.scan_lstw.currentRow()
        scan = self.project.scans[i]

        gridding_options_sbxs = [
            self.h_min_sbx, self.h_max_sbx, self.h_n_sbx,
            self.k_min_sbx, self.k_max_sbx, self.k_n_sbx,
            self.l_min_sbx, self.l_max_sbx, self.l_n_sbx,
        ]
        original_params = [
            np.amin(scan.h_map), np.amax(scan.h_map), 250,
            np.amin(scan.k_map), np.amax(scan.k_map), 250,
            np.amin(scan.l_map), np.amax(scan.l_map), 250,
        ]

        for sbx, o_param in zip(gridding_options_sbxs, original_params):
            sbx.setValue(round(o_param, 3))

        # Enable "Load Scan" button
        self.load_scan_btn.setEnabled(True)

    def loadScan(self) -> None:
        """Loads scan data into a new DataView tab."""

        # Retrieves current scan
        i = self.scan_lstw.currentRow()
        scan = self.project.scans[i]

        sbxs = [
            self.h_min_sbx, self.h_max_sbx, self.h_n_sbx,
            self.k_min_sbx, self.k_max_sbx, self.k_n_sbx,
            self.l_min_sbx, self.l_max_sbx, self.l_n_sbx,
        ]

        # Checks if spinbox mins/maxes are valid
        if (
            sbxs[0].value() < sbxs[1].value() and
            sbxs[3].value() < sbxs[4].value() and
            sbxs[6].value() < sbxs[7].value()
        ):
            scan.setGriddingParameters(*(float(sbx.value()) for sbx in sbxs))
            scan.gridImageData()
            self.main_window.data_view.addScan(scan)
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Invalid gridding bounds.")
            msg.exec_()
