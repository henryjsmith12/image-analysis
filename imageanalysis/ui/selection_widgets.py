"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from PyQt5 import QtWidgets
from pyqtgraph import QtCore

from imageanalysis.io import \
    isValidProjectPath, getSPECPaths, getXMLPaths
from imageanalysis.structures import Project, Scan

class ProjectSelectionWidget(QtWidgets.QWidget):
    """QtWidget that allows user to:
    
        - Select a project directory
        - Select associated configuration files
        - Load project from directory
    """

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

        # Widget options
        self.select_project_btn.setDefault(True)
        self.select_project_txt.setReadOnly(True)
        self._hideProjectFileSelectionWidgets()

        # Layout
        self.layout = QtWidgets.QGridLayout()
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
    """QtWidget that allows user to:

        - Select scans to load
        - Select gridding interpolation for scans
        - View basic metadata about scans
    """

    main_window = None # Main window of application
    project = None # Current project loaded in selection widget

    scan_table = None # Table widget with scan information
    scan_table_items = None # Scan items in table widget
    preview_table = None # Groupbox to hold basic scan preview information
    load_selected_scans_btn = None # Button to load all selected scans
    
    layout = None # Grid layout

    def __init__(self, parent) -> None:
        super(ScanSelectionWidget, self).__init__()

        self.main_window = parent

        self.project = None

        # Widgets
        self.scan_table = QtWidgets.QTableWidget(0, 4)
        self.preview_table = QtWidgets.QTableWidget(8, 1)
        self.load_selected_scan_btn = QtWidgets.QPushButton("Load Scan")

        # Widget options
        self.setEnabled(False)
        self.scan_table.setHorizontalHeaderLabels(["Scan", "nPts", "Type", ""])
        self.scan_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
        self.scan_table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents)
        self.scan_table.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents)
        self.scan_table.horizontalHeader().setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)
        self.scan_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.preview_table.setHorizontalHeaderLabels([""])
        self.preview_table.setVerticalHeaderLabels(["Scan", "nPts", "Start Value", "End Value", "Grid Size", "H Grid Bounds", "K Grid Bounds", "L Grid Bounds"])
        self.preview_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        
        # Layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.scan_table, 0, 0, 3, 12)
        self.layout.addWidget(self.preview_table, 3, 0, 4, 12)
        self.layout.addWidget(self.load_selected_scan_btn, 7, 0, 1, 12)

        # Connections
        self.scan_table.cellClicked.connect(self._previewScan)
        self.scan_table.entered.connect(self._previewScan)
        self.load_selected_scan_btn.clicked.connect(self._loadScan)

    def _loadProject(self, project: Project) -> None:
        self.setEnabled(True)

        self.project = project

        self.scan_table.setRowCount(0)
        self.scan_table_items = []

        for scan_number in project.scans.keys():
            scan = project.scans[scan_number]
            scan.map()
            self._addScanToTable(scan=scan)

    def _addScanToTable(self, scan: Scan) -> None:
        sti = ScanSelectionWidgetItem(parent=self, scan=scan)
        self.scan_table_items.append(sti)
        i = self.scan_table_items.index(sti)

        self.scan_table.insertRow(self.scan_table.rowCount())
        self.scan_table.setCellWidget(i, 0, sti.scan_number_lbl)
        self.scan_table.setCellWidget(i, 1, sti.n_pts_lbl)
        self.scan_table.setCellWidget(i, 2, sti.scan_type_lbl)
        self.scan_table.setCellWidget(i, 3, sti.options_btn)
        
    def _previewScan(self) -> None:
        """Displays preview information for a Scan object."""

        i = self.scan_table.currentRow()
        scan = self.scan_table_items[i].scan
        start_value = scan.spec_scan.data[scan.spec_scan.L[0]][0]
        end_value = scan.spec_scan.data[scan.spec_scan.L[0]][-1]
        grid_params = scan.grid_params
        h_min, h_max = grid_params["H"]["min"], grid_params["H"]["max"]
        k_min, k_max = grid_params["K"]["min"], grid_params["K"]["max"]
        l_min, l_max = grid_params["L"]["min"], grid_params["L"]["max"]
        h_n, k_n, l_n = grid_params["H"]["n"], grid_params["K"]["n"], grid_params["L"]["n"]
        grid_size = f"({h_n}, {k_n}, {l_n})"
        h_bounds = f"({round(h_min, 5)}, {round(h_max, 5)})"
        k_bounds = f"({round(k_min, 5)}, {round(k_max, 5)})"
        l_bounds = f"({round(l_min, 5)}, {round(l_max, 5)})"

        self.preview_table.setCellWidget(0, 0, QtWidgets.QLabel(str(scan.number)))
        self.preview_table.setCellWidget(1, 0, QtWidgets.QLabel(str(scan.n_pts)))
        self.preview_table.setCellWidget(2, 0, QtWidgets.QLabel(str(start_value)))
        self.preview_table.setCellWidget(3, 0, QtWidgets.QLabel(str(end_value)))
        self.preview_table.setCellWidget(4, 0, QtWidgets.QLabel(grid_size))
        self.preview_table.setCellWidget(5, 0, QtWidgets.QLabel(h_bounds))
        self.preview_table.setCellWidget(6, 0, QtWidgets.QLabel(k_bounds))
        self.preview_table.setCellWidget(7, 0, QtWidgets.QLabel(l_bounds))
        
    def _loadScan(self) -> None:
        """Prepares and loads a Scan into the DataView."""

        i = self.scan_table.currentRow()
        scan_item = self.scan_table_items[i]
        scan = scan_item.scan    
        scan.loadRawData()
        scan.grid()
        self.main_window.data_view._addScan(scan=scan)
        self.main_window.plot_view.setEnabled(True)


class ScanSelectionWidgetItem:

    selected_chkbx = None
    scan_number_lbl = None
    n_pts_lbl = None
    scan_type_lbl = None
    options_btn = None

    options_dialog = None # Dialog for gridding options

    def __init__(self, parent, scan):
        
        self.parent = parent
        self.scan = scan

        # Widgets
        self.selected_chkbx = QtWidgets.QCheckBox()
        self.scan_number_lbl = QtWidgets.QLabel()
        self.n_pts_lbl = QtWidgets.QLabel()
        self.scan_type_lbl = QtWidgets.QLabel()
        self.options_btn = QtWidgets.QPushButton("Options")

        self.options_dialog = ScanOptionsDialogWidget(scan)

        self.selected_chkbx.setChecked(False)
        self.scan_number_lbl.setText(str(self.scan.number))
        self.n_pts_lbl.setText(str(self.scan.n_pts))
        scan_type_comps = str.split(self.scan.spec_scan.scanCmd, " ")
        scan_type = f"{scan_type_comps[0]}  {scan_type_comps[2]}"
        self.scan_type_lbl.setText(scan_type)

        # Widget options
        self.scan_number_lbl.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        self.n_pts_lbl.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        self.scan_type_lbl.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )

        # Connections
        self.options_btn.clicked.connect(self._setOptions)

    def _setOptions(self) -> None:
        self.options_dialog.exec_()
        self.parent._previewScan()


class ScanOptionsDialogWidget(QtWidgets.QDialog):

    scan = None
    grid_options = None

    grid_options_gbx = None
    grid_options_table = None
    grid_h_min_sbx = None
    grid_h_max_sbx = None
    grid_h_n_sbx = None
    grid_k_min_sbx = None
    grid_k_max_sbx = None
    grid_k_n_sbx = None
    grid_l_min_sbx = None
    grid_l_max_sbx = None
    grid_l_n_sbx = None
    save_options_btn = None
    layout = None
    grid_options_gbx_layout = None
    
    def __init__(self, scan) -> None:
        super(ScanOptionsDialogWidget, self).__init__()

        self.scan = scan
        self.grid_options = scan.grid_params

        # Widgets
        self.grid_options_gbx = QtWidgets.QGroupBox()
        self.grid_options_table = QtWidgets.QTableWidget(3, 3)
        self.grid_h_min_sbx = QtWidgets.QDoubleSpinBox()
        self.grid_h_max_sbx = QtWidgets.QDoubleSpinBox()
        self.grid_h_n_sbx = QtWidgets.QSpinBox()
        self.grid_k_min_sbx = QtWidgets.QDoubleSpinBox()
        self.grid_k_max_sbx = QtWidgets.QDoubleSpinBox()
        self.grid_k_n_sbx = QtWidgets.QSpinBox()
        self.grid_l_min_sbx = QtWidgets.QDoubleSpinBox()
        self.grid_l_max_sbx = QtWidgets.QDoubleSpinBox()
        self.grid_l_n_sbx = QtWidgets.QSpinBox()
        self.reset_btn = QtWidgets.QPushButton("Reset")
        self.save_options_btn = QtWidgets.QPushButton("Save Options")
        
        # Widget options
        self.grid_options_table.setCellWidget(0, 0, self.grid_h_min_sbx)
        self.grid_options_table.setCellWidget(0, 1, self.grid_h_max_sbx)
        self.grid_options_table.setCellWidget(0, 2, self.grid_h_n_sbx)
        self.grid_options_table.setCellWidget(1, 0, self.grid_k_min_sbx)
        self.grid_options_table.setCellWidget(1, 1, self.grid_k_max_sbx)
        self.grid_options_table.setCellWidget(1, 2, self.grid_k_n_sbx)
        self.grid_options_table.setCellWidget(2, 0, self.grid_l_min_sbx)
        self.grid_options_table.setCellWidget(2, 1, self.grid_l_max_sbx)
        self.grid_options_table.setCellWidget(2, 2, self.grid_l_n_sbx)

        self.grid_options_table.setHorizontalHeaderLabels(["Min", "Max", "nPts"])
        self.grid_options_table.setVerticalHeaderLabels(["H", "K", "L"])
        self.grid_options_table.horizontalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self.grid_options_table.horizontalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        self.grid_options_table.horizontalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)
        self.grid_options_table.verticalHeader().setSectionResizeMode(
            0, QtWidgets.QHeaderView.Stretch)
        self.grid_options_table.verticalHeader().setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)
        self.grid_options_table.verticalHeader().setSectionResizeMode(
            2, QtWidgets.QHeaderView.Stretch)
        
        self.grid_h_min_sbx.setMinimum(-100.0)
        self.grid_h_min_sbx.setMaximum(100.0)
        self.grid_h_min_sbx.setDecimals(5)
        self.grid_h_max_sbx.setMinimum(-100.0)
        self.grid_h_max_sbx.setMaximum(100.0)
        self.grid_h_max_sbx.setDecimals(5)
        self.grid_h_n_sbx.setMinimum(10)
        self.grid_h_n_sbx.setMaximum(750)
        self.grid_k_min_sbx.setMinimum(-100.0)
        self.grid_k_min_sbx.setMaximum(100.0)
        self.grid_k_min_sbx.setDecimals(5)
        self.grid_k_max_sbx.setMinimum(-100.0)
        self.grid_k_max_sbx.setMaximum(100.0)
        self.grid_k_max_sbx.setDecimals(5)
        self.grid_k_n_sbx.setMinimum(10)
        self.grid_k_n_sbx.setMaximum(750)
        self.grid_l_min_sbx.setMinimum(-100.0)
        self.grid_l_min_sbx.setMaximum(100.0)
        self.grid_l_min_sbx.setDecimals(5)
        self.grid_l_max_sbx.setMinimum(-100.0)
        self.grid_l_max_sbx.setMaximum(100.0)
        self.grid_l_max_sbx.setDecimals(5)
        self.grid_l_n_sbx.setMinimum(10)
        self.grid_l_n_sbx.setMaximum(750)

        self.reset_btn.setDefault(False)
        
        # Layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.grid_options_gbx, 0, 0, 1, 2)
        self.layout.addWidget(self.save_options_btn, 1, 0, 1, 2)
        self.layout.addWidget(self.reset_btn, 2, 0, 1, 2)

        # Grid options layout
        self.grid_options_gbx_layout = QtWidgets.QGridLayout()
        self.grid_options_gbx.setLayout(self.grid_options_gbx_layout)
        self.grid_options_gbx_layout.addWidget(self.grid_options_table)

        # Connections
        self.reset_btn.clicked.connect(self._resetOptions)
        self.save_options_btn.clicked.connect(self.accept)

        self._resetOptions()

    def _resetOptions(self) -> None:
        self.grid_options = self.scan.grid_params
        self.grid_h_min_sbx.setValue(self.grid_options["H"]["min"])
        self.grid_h_max_sbx.setValue(self.grid_options["H"]["max"])
        self.grid_h_n_sbx.setValue(self.grid_options["H"]["n"])
        self.grid_k_min_sbx.setValue(self.grid_options["K"]["min"])
        self.grid_k_max_sbx.setValue(self.grid_options["K"]["max"])
        self.grid_k_n_sbx.setValue(self.grid_options["K"]["n"])
        self.grid_l_min_sbx.setValue(self.grid_options["L"]["min"])
        self.grid_l_max_sbx.setValue(self.grid_options["L"]["max"])
        self.grid_l_n_sbx.setValue(self.grid_options["L"]["n"])
        
    def _validateOptions(self) -> None:
        ...

    def accept(self) -> None:
        self.grid_options = {
            "H": {
                "min": self.grid_h_min_sbx.value(), 
                "max": self.grid_h_max_sbx.value(), 
                "n": self.grid_h_n_sbx.value()
            },
            "K": {
                "min": self.grid_k_min_sbx.value(), 
                "max": self.grid_k_max_sbx.value(), 
                "n": self.grid_k_n_sbx.value()
            },
            "L": {
                "min": self.grid_l_min_sbx.value(), 
                "max": self.grid_l_max_sbx.value(), 
                "n": self.grid_l_n_sbx.value()
            }
        }

        self.scan.setGridSize(
            self.grid_options["H"]["n"],
            self.grid_options["K"]["n"],
            self.grid_options["L"]["n"]
        )
        self.scan.setGridBounds(
            self.grid_options["H"]["min"],
            self.grid_options["H"]["max"],
            self.grid_options["K"]["min"],
            self.grid_options["K"]["max"],
            self.grid_options["L"]["min"],
            self.grid_options["L"]["max"]
        )
        return super().accept()