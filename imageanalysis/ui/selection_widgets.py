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

    main_window = None # Main window of application
    project_path = None # Absolute path of project directory
    spec_path = None # Absolute path of project SPEC file
    instrument_path = None # Absolute path of project instrument config XML
    detector_path = None # Absolute path of project detector config XML

    select_project_btn = None # Button for opening directory selection UI
    select_project_txt = None # TextBox to display selected project directory
    spec_lbl = None # "SPEC Source"
    spec_cbx = None # ComboBox with available SPEC files in project directory
    instrument_lbl = None # "Instrument"
    instrument_cbx = None # ComboBox with XML files in project directory
    detector_lbl = None # "Detector"
    detector_cbx = None # ComboBox with XML files in project directory
    clear_project_btn = None # Button for clearing project/scan selection areas
    load_project_btn = None # Button for loading selected project
    layout = None # Grid layout

    def __init__(self, parent) -> None:
        super(ProjectSelectionWidget, self).__init__()

        self.main_window = parent

        # Widgets
        self.select_project_btn = QtWidgets.QPushButton("Select Project")
        self.select_project_txt = QtWidgets.QLineEdit()
        self.spec_lbl = QtWidgets.QLabel("SPEC Source:")
        self.spec_cbx = QtWidgets.QComboBox()
        self.instrument_lbl = QtWidgets.QLabel("Instrument:")
        self.instrument_cbx = QtWidgets.QComboBox()
        self.detector_lbl = QtWidgets.QLabel("Detector:")
        self.detector_cbx = QtWidgets.QComboBox()
        self.load_project_btn = QtWidgets.QPushButton("Load Project")
        self.layout = QtWidgets.QGridLayout()

        # Widget options
        self.select_project_btn.setDefault(True)
        self.select_project_txt.setReadOnly(True)
        self._hideProjectFileSelectionWidgets()

        # Layout
        self.setLayout(self.layout)
        self.layout.addWidget(self.select_project_btn, 0, 0, 1, 5)
        self.layout.addWidget(self.select_project_txt, 0, 5, 1, 7)
        self.layout.addWidget(self.spec_lbl, 1, 0, 1, 4)
        self.layout.addWidget(self.spec_cbx, 1, 4, 1, 8)
        self.layout.addWidget(self.instrument_lbl, 2, 0, 1, 4)
        self.layout.addWidget(self.instrument_cbx, 2, 4, 1, 8)
        self.layout.addWidget(self.detector_lbl, 3, 0, 1, 4)
        self.layout.addWidget(self.detector_cbx, 3, 4, 1, 8)
        self.layout.addWidget(self.load_project_btn, 4, 0, 1, 12)

        # Layout options
        for i in range(12):
            self.layout.setColumnStretch(i, 1)
        for i in range(4):
            self.layout.setRowStretch(i, 1)

        # Connections
        self.select_project_btn.clicked.connect(self._selectProject)
        self.load_project_btn.clicked.connect(self._loadProject)

    def _selectProject(self) -> None:
        """Allows user to select a project directory.
        
        - Opens directory selection dialog
        - If valid project, displays project file selection comboboxes
        - If invalid project, displays error dialog
        """

        project_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Project"
        )

        # Omits empty paths from cancelling out of file dialog
        if project_path != "":
            # Checks if project path is valid
            if isValidProjectPath(project_path):
                self.project_path = project_path
                self.select_project_txt.setText(project_path)
                self._addSPECFilesToComboBox()
                self._addInstrumentFilesToComboBox()
                self._addDetectorFilesToComboBox()
                self._showProjectFileSelectionWidgets()
                self.select_project_btn.setDefault(False)
                self.load_project_btn.setDefault(True)
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("Invalid project directory.")
                msg.exec_()

    def _addSPECFilesToComboBox(self) -> None:
        """Adds valid SPEC files to combobox."""
        
        spec_paths = getSPECPaths(self.project_path) 
        self.spec_cbx.clear()
        self.spec_cbx.addItems(spec_paths)

    def _addInstrumentFilesToComboBox(self) -> None:
        """Adds valid XML files to combobox."""

        xml_paths = getXMLPaths(self.project_path)
        self.instrument_cbx.clear()
        self.instrument_cbx.addItems(xml_paths)

        for i in range(len(xml_paths)):
            if "Instrument" in str(xml_paths[i]) or \
                "instrument" in str(xml_paths[i]):
                self.instrument_cbx.setCurrentIndex(i)
                break

    def _addDetectorFilesToComboBox(self) -> None:
        """Adds valid XML files to combobox."""

        xml_paths = getXMLPaths(self.project_path)
        self.detector_cbx.clear()
        self.detector_cbx.addItems(xml_paths)

        for i in range(len(xml_paths)):
            if "Detector" in str(xml_paths[i]) or \
                "detector" in str(xml_paths[i]):
                self.detector_cbx.setCurrentIndex(i)
                break

    def _showProjectFileSelectionWidgets(self) -> None:
        """Makes project file widgets visible."""

        self.spec_lbl.show()
        self.spec_cbx.show()
        self.instrument_lbl.show()
        self.instrument_cbx.show()
        self.detector_lbl.show()
        self.detector_cbx.show()
        self.load_project_btn.show()

    def _hideProjectFileSelectionWidgets(self) -> None:
        """Hides project file widgets."""

        self.spec_lbl.hide()
        self.spec_cbx.hide()
        self.instrument_lbl.hide()
        self.instrument_cbx.hide()
        self.detector_lbl.hide()
        self.detector_cbx.hide()
        self.load_project_btn.hide()

    def _setProjectFiles(self) -> None:
        """Sets absolute paths for project files."""

        self.spec_path = f"{self.project_path}/" \
            f"{self.spec_cbx.currentText()}"
        self.instrument_path = f"{self.project_path}/" \
            f"{self.instrument_cbx.currentText()}"
        self.detector_path = f"{self.project_path}/" \
            f"{self.detector_cbx.currentText()}"

    def _loadProject(self) -> None:
        """Creates and loads Project object."""

        self._setProjectFiles()
        
        # Creates Project with given file paths
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
        self.scan_lstw.addItems([str(key) for key in self.project.scans.keys()])

    def _getCurrentScan(self) -> Scan:
        """Returns Scan object of currently highlighted scan number."""
        scan_number = int(self.scan_lstw.currentItem().text())
        scan = self.project.scans[scan_number]
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
            scan.map()
            scan._setGridParametersToRSM()

        h_min = scan.grid_params["H"]["min"]
        k_min = scan.grid_params["K"]["min"]
        l_min = scan.grid_params["L"]["min"]
        h_max = scan.grid_params["H"]["max"]
        k_max = scan.grid_params["K"]["max"]
        l_max = scan.grid_params["L"]["max"]
        h_n = scan.grid_params["H"]["n"]
        k_n = scan.grid_params["K"]["n"]
        l_n = scan.grid_params["L"]["n"]
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
            scan.setGridSize(self.h_n_sbx.value(), self.k_n_sbx.value(), self.l_n_sbx.value())
            scan.setGridBounds(
                self.h_min_sbx.value(), self.h_max_sbx.value(),
                self.k_min_sbx.value(), self.k_max_sbx.value(),
                self.l_min_sbx.value(), self.l_max_sbx.value()
            )

            scan.loadRawData()
            scan.grid()
            self.main_window.data_view._addScan(scan=scan)
            self.main_window.plot_view.setEnabled(True)
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("Invalid gridding bounds.")
            msg.exec_()
