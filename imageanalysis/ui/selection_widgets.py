"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from PyQt5 import QtWidgets
from pyqtgraph import QtCore

from imageanalysis.io import \
    isValidProjectPath, getSPECPaths, getXMLPaths
from imageanalysis.structures import Project, Scan


class ProjectSelectionWidget(QtWidgets.QWidget):
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
        self.project_btn = QtWidgets.QPushButton("Select Project")
        self.project_txt = QtWidgets.QLineEdit()
        self.project_txt.setReadOnly(True)
        self.project_files_gbx = QtWidgets.QGroupBox()
        self.project_files_gbx.setEnabled(False)
        self.spec_lbl = QtWidgets.QLabel("SPEC Source:")
        self.spec_cbx = QtWidgets.QComboBox()
        self.instrument_lbl = QtWidgets.QLabel("Instrument:")
        self.instrument_cbx = QtWidgets.QComboBox()
        self.detector_lbl = QtWidgets.QLabel("Detector:")
        self.detector_cbx = QtWidgets.QComboBox()
        self.load_project_btn = QtWidgets.QPushButton("Load Project")
        self.load_project_btn.setEnabled(False)

        # Project files GroupBox layout
        self.project_files_gbx_layout = QtWidgets.QGridLayout()
        self.project_files_gbx.setLayout(self.project_files_gbx_layout)
        self.project_files_gbx_layout.addWidget(self.spec_lbl, 0, 0)
        self.project_files_gbx_layout.addWidget(self.spec_cbx, 0, 1, 1, 2)
        self.project_files_gbx_layout.addWidget(self.instrument_lbl, 1, 0)
        self.project_files_gbx_layout.addWidget(self.instrument_cbx, 1, 1, 1, 2)
        self.project_files_gbx_layout.addWidget(self.detector_lbl, 2, 0)
        self.project_files_gbx_layout.addWidget(self.detector_cbx, 2, 1, 1, 2)
        self.project_files_gbx_layout.addWidget(self.load_project_btn, 3, 0, 1, 3)

        # Main layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.project_btn, 0, 0)
        self.layout.addWidget(self.project_txt, 0, 1)
        self.layout.addWidget(self.project_files_gbx, 1, 0, 1, 2)

        # Connections
        self.project_btn.clicked.connect(self._selectProject)
        self.spec_cbx.currentTextChanged.connect(
            self._enableLoadProjectButton
        )
        self.instrument_cbx.currentTextChanged.connect(
            self._enableLoadProjectButton
        )
        self.detector_cbx.currentTextChanged.connect(
            self._enableLoadProjectButton
        )
        self.load_project_btn.clicked.connect(self._loadProject)

    def _selectProject(self) -> None:
        """Allows user to select a project directory."""

        project_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Project"
        )

        # Omits empty paths from cancelling out of file dialog
        if project_path != "":
            # Checks if project path is valid
            if isValidProjectPath(project_path):
                self.project_path = project_path
                self.project_txt.setText(project_path)
                self.project_files_gbx.setEnabled(True)
                self._populateProjectFilesGroupbox()
            else:
                self.project_files_gbx.setEnabled(False)
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("Invalid project directory.")
                msg.exec_()

    def _populateProjectFilesGroupbox(self) -> None:
        """Adds SPEC files and XML files to comboboxes."""

        self.spec_cbx.clear()
        self.instrument_cbx.clear()
        self.detector_cbx.clear()

        spec_paths = getSPECPaths(self.project_path)
        xml_paths = getXMLPaths(self.project_path)

        self.spec_cbx.addItems(spec_paths)
        self.instrument_cbx.addItems(xml_paths)
        self.detector_cbx.addItems(xml_paths)

        for i in range(len(xml_paths)):
            if "Instrument" in str(xml_paths[i]) or "instrument" in str(xml_paths[i]):
                self.instrument_cbx.setCurrentIndex(i)
            if "Detector" in str(xml_paths[i]) or "detector" in str(xml_paths[i]):
                self.detector_cbx.setCurrentIndex(i)

    def _enableLoadProjectButton(self) -> None:
        """Sets path variables and enables 'Load Project' button."""

        self.spec_path = f"{self.project_path}/" \
            f"{self.spec_cbx.currentText()}"
        self.instrument_path = f"{self.project_path}/" \
            f"{self.instrument_cbx.currentText()}"
        self.detector_path = f"{self.project_path}/" \
            f"{self.detector_cbx.currentText()}"

        self.load_project_btn.setEnabled(True)

    def _loadProject(self) -> None:
        """Creates and loads Project object."""

        # Attempts to create and load Project with given file paths
        project = Project(
            project_path=self.project_path,
            spec_path=self.spec_path,
            instrument_path=self.instrument_path,
            detector_path=self.detector_path
        )
        self.project = project
        self.main_window.scan_selection_widget._loadProject(project)


class ScanSelectionWidget(QtWidgets.QWidget):
    """Handles scan selection and loading."""

    def __init__(self, parent) -> None:
        super(ScanSelectionWidget, self).__init__()

        self.main_window = parent

        # Project
        self.project = None

        # Child widgets
        self.scan_lstw = QtWidgets.QListWidget()
        self.scan_details_gbx = QtWidgets.QGroupBox()
        self.scan_details_gbx.setEnabled(False)
        self.scan_number_lbl = QtWidgets.QLabel("Scan:")
        self.scan_number_txt = QtWidgets.QLineEdit()
        self.scan_number_txt.setReadOnly(True)
        self.scan_point_count_lbl = QtWidgets.QLabel("# Points:")
        self.scan_point_count_txt = QtWidgets.QLineEdit()
        self.scan_point_count_txt.setReadOnly(True)
        self.scan_date_lbl = QtWidgets.QLabel()
        self.scan_date_lbl.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        self.scan_type_lbl = QtWidgets.QLabel()
        self.scan_type_lbl.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        self.scan_bounds_lbl = QtWidgets.QLabel()
        self.scan_bounds_lbl.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        self.gridding_options_gbx = QtWidgets.QGroupBox()
        self.gridding_options_gbx.setTitle("Gridding Options")
        self.min_lbl = QtWidgets.QLabel("Min")
        self.max_lbl = QtWidgets.QLabel("Max")
        self.n_lbl = QtWidgets.QLabel("n")
        self.h_lbl = QtWidgets.QLabel("H:")
        self.h_min_sbx = QtWidgets.QDoubleSpinBox()
        self.h_max_sbx = QtWidgets.QDoubleSpinBox()
        self.h_n_sbx = QtWidgets.QSpinBox()
        self.k_lbl = QtWidgets.QLabel("K:")
        self.k_min_sbx = QtWidgets.QDoubleSpinBox()
        self.k_max_sbx = QtWidgets.QDoubleSpinBox()
        self.k_n_sbx = QtWidgets.QSpinBox()
        self.l_lbl = QtWidgets.QLabel("L:")
        self.l_min_sbx = QtWidgets.QDoubleSpinBox()
        self.l_max_sbx = QtWidgets.QDoubleSpinBox()
        self.l_n_sbx = QtWidgets.QSpinBox()
        self.reset_btn = QtWidgets.QPushButton("Reset")
        self.load_scan_btn = QtWidgets.QPushButton("Load Scan")

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
            sbx.setRange(10, 750)

        # Scan details GroupBox layout
        self.scan_details_gbx_layout = QtWidgets.QGridLayout()
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
            self.scan_type_lbl, 2, 0, 1, 2)
        self.scan_details_gbx_layout.addWidget(
            self.scan_bounds_lbl, 2, 2, 1, 2)
        self.scan_details_gbx_layout.addWidget(
            self.gridding_options_gbx, 3, 0, 1, 4)
        self.scan_details_gbx_layout.addWidget(
            self.load_scan_btn, 4, 2, 1, 2)

        # gridding options GroupBox layout
        self.gridding_options_gbx_layout = QtWidgets.QGridLayout()
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
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.scan_lstw, 0, 0)
        self.layout.addWidget(self.scan_details_gbx, 1, 0)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 2)

        # Connections
        self.scan_lstw.itemClicked.connect(self._previewScan)
        self.reset_btn.clicked.connect(self._resetScanGridParameters)
        self.load_scan_btn.clicked.connect(self._loadScan)

    def _loadProject(self, project: Project) -> None:
        """Sets project variable and loads scan numbers in list."""
        self.project = project
        self.scan_lstw.clear()
        self.scan_lstw.addItems(self.project._getScanNumbers())

    def _getCurrentScan(self) -> Scan:
        """Returns Scan object of currently highlighted scan number."""
        scan_number = int(self.scan_lstw.currentItem().text())
        scan = self.project.getScan(scan_number)
        return scan

    def _previewScan(self, scan=None) -> None:
        """Displays preview information for a Scan object."""
        self.scan_details_gbx.setEnabled(True)

        scan = self._getCurrentScan()

        # Scan metadata
        header = scan.spec_scan.S.split()
        number = header[0]
        type = f"{header[1]} {header[2]}"
        bounds = f"({header[3]}, {header[4]})"
        point_count = str(len(scan.spec_scan.data_lines))
        date = scan.spec_scan.date
        self.scan_number_txt.setText(number)
        self.scan_point_count_txt.setText(point_count)
        self.scan_date_lbl.setText(date)
        self.scan_type_lbl.setText(type)
        self.scan_bounds_lbl.setText(bounds)

        # Scan grid parameters
        if scan.rsm is None:
            scan._mapRawImageData()
        h_min = scan.grid_parameters["H"]["min"]
        k_min = scan.grid_parameters["K"]["min"]
        l_min = scan.grid_parameters["L"]["min"]
        h_max = scan.grid_parameters["H"]["max"]
        k_max = scan.grid_parameters["K"]["max"]
        l_max = scan.grid_parameters["L"]["max"]
        h_n = scan.grid_parameters["H"]["n"]
        k_n = scan.grid_parameters["K"]["n"]
        l_n = scan.grid_parameters["L"]["n"]
        self.h_min_sbx.setValue(h_min)
        self.h_max_sbx.setValue(h_max)
        self.h_n_sbx.setValue(h_n)
        self.k_min_sbx.setValue(k_min)
        self.k_max_sbx.setValue(k_max)
        self.k_n_sbx.setValue(k_n)
        self.l_min_sbx.setValue(l_min)
        self.l_max_sbx.setValue(l_max)
        self.l_n_sbx.setValue(l_n)

    def _resetScanGridParameters(self) -> None:
        """Resets grid parameters for a scan object."""
        scan = self._getCurrentScan()
        scan._resetGridParameters()
        self._previewScan()

    def _loadScan(self) -> None:
        """Prepares and loads a Scan into the DataView."""
        if (
            self.h_min_sbx.value() < self.h_max_sbx.value() and
            self.k_min_sbx.value() < self.k_max_sbx.value() and
            self.l_min_sbx.value() < self.l_max_sbx.value()
        ):
            grid_params = {
                "H": {
                    "min": self.h_min_sbx.value(),
                    "max": self.h_max_sbx.value(),
                    "n": self.h_n_sbx.value()
                },
                "K": {
                    "min": self.k_min_sbx.value(),
                    "max": self.k_max_sbx.value(),
                    "n": self.k_n_sbx.value()
                },
                "L": {
                    "min": self.l_min_sbx.value(),
                    "max": self.l_max_sbx.value(),
                    "n": self.l_n_sbx.value()
                }
            }

            scan = self._getCurrentScan()
            scan._setGridParameters(params=grid_params)

            scan._loadRawImageData()
            scan._gridRawImageData()
            self.main_window.data_view._addScan(scan=scan)
            self.main_window.plot_view.setEnabled(True)
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Invalid gridding bounds.")
            msg.exec_()
