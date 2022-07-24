"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import numpy as np
from pyqtgraph import QtGui

from imageanalysis.io import isValidProjectPath, getSPECPaths, getXMLPaths
from imageanalysis.structures import Project

# ==================================================================================

class ProjectSelectionWidget(QtGui.QWidget):
    """
    Allows user to open a project.
    """

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
        self.clear_project_btn = QtGui.QPushButton("Clear Project")
        self.clear_project_btn.setEnabled(False)
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
        self.project_files_gbx_layout.addWidget(self.clear_project_btn, 3, 0)
        self.project_files_gbx_layout.addWidget(self.load_project_btn, 3, 1)

        # Main layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.project_btn, 0, 0)
        self.layout.addWidget(self.project_txt, 0, 1)
        self.layout.addWidget(self.project_files_gbx, 1, 0, 1, 2)

        # Connections
        self.project_btn.clicked.connect(self.selectProject)
        self.spec_cbx.currentTextChanged.connect(self.enableLoadProjectButton)
        self.instrument_cbx.currentTextChanged.connect(self.enableLoadProjectButton)
        self.detector_cbx.currentTextChanged.connect(self.enableLoadProjectButton)
        self.load_project_btn.clicked.connect(self.loadProject)

    # ------------------------------------------------------------------------------

    def selectProject(self):
        """
        Allows user to select a directory with a file dialog and then validates the 
        selected directory.
        """

        project_path = QtGui.QFileDialog.getExistingDirectory(self, "Select Project")

        if isValidProjectPath(project_path):
            self.project_path = project_path
            self.project_txt.setText(project_path)
            self.project_files_gbx.setEnabled(True)
            self.populateProjectFilesGroupbox()

    # ------------------------------------------------------------------------------

    def populateProjectFilesGroupbox(self):
        """
        Adds SPEC sources and XML configuration files to comboboxes.
        """

        spec_paths = [""] + getSPECPaths(self.project_path)
        xml_paths = [""] + getXMLPaths(self.project_path)


        self.spec_cbx.addItems(spec_paths)
        self.instrument_cbx.addItems(xml_paths)
        self.detector_cbx.addItems(xml_paths)

    # ------------------------------------------------------------------------------

    def enableLoadProjectButton(self):
        """
        Checks if all project file comboboxes are nonempty and enabled "Load Project"
        option.
        """

        self.spec_path = f"{self.project_path}/{self.spec_cbx.currentText()}"
        self.instrument_path = f"{self.project_path}/{self.instrument_cbx.currentText()}"
        self.detector_path = f"{self.project_path}/{self.detector_cbx.currentText()}"

        if "/" not in [self.spec_path[-1], self.instrument_path[-1], self.detector_path[-1]]:
            self.load_project_btn.setEnabled(True)
        else:
            self.load_project_btn.setEnabled(False)

    # ------------------------------------------------------------------------------

    def loadProject(self):
        """
        Create Project object from given paths and load information into the 
        ScanSelectionWidget.
        """

        self.project = Project(
            project_path=self.project_path,
            spec_path=self.spec_path,
            instrument_path=self.instrument_path,
            detector_path=self.detector_path
        )

        self.main_window.scan_selection_widget.loadProjectScanList(self.project)

# ==================================================================================

class ScanSelectionWidget(QtGui.QWidget):
    """
    Displays available scans in a Project and allows user to select a specific scan
    to display information from.
    """

    def __init__(self, parent) -> None:
        super(ScanSelectionWidget, self).__init__()

        self.main_window = parent

        # Project
        self.project = None

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
        self.h_min_txt = QtGui.QLineEdit()
        self.h_max_txt = QtGui.QLineEdit()
        self.h_n_txt = QtGui.QLineEdit()
        self.k_lbl = QtGui.QLabel("K:")
        self.k_min_txt = QtGui.QLineEdit()
        self.k_max_txt = QtGui.QLineEdit()
        self.k_n_txt = QtGui.QLineEdit()
        self.l_lbl = QtGui.QLabel("L:")
        self.l_min_txt = QtGui.QLineEdit()
        self.l_max_txt = QtGui.QLineEdit()
        self.l_n_txt = QtGui.QLineEdit()
        self.load_scan_btn = QtGui.QPushButton("Load Scan")
        
        # Scan details GroupBox layout
        self.scan_details_gbx_layout = QtGui.QGridLayout()
        self.scan_details_gbx.setLayout(self.scan_details_gbx_layout)
        self.scan_details_gbx_layout.addWidget(self.scan_number_lbl, 0, 0)
        self.scan_details_gbx_layout.addWidget(self.scan_number_txt, 0, 1)
        self.scan_details_gbx_layout.addWidget(self.scan_point_count_lbl, 0, 2)
        self.scan_details_gbx_layout.addWidget(self.scan_point_count_txt, 0, 3)
        self.scan_details_gbx_layout.addWidget(self.scan_date_lbl, 1, 0, 1, 4)
        self.scan_details_gbx_layout.addWidget(self.scan_type_lbl, 2, 0)
        self.scan_details_gbx_layout.addWidget(self.scan_bounds_lbl, 2, 1, 1, 3)
        self.scan_details_gbx_layout.addWidget(self.gridding_options_gbx, 3, 0, 1, 4)
        self.scan_details_gbx_layout.addWidget(self.load_scan_btn, 4, 2, 1, 2)

        # gridding options GroupBox layout
        self.gridding_options_gbx_layout = QtGui.QGridLayout()
        self.gridding_options_gbx.setLayout(self.gridding_options_gbx_layout)
        self.gridding_options_gbx_layout.addWidget(self.min_lbl, 0, 1)
        self.gridding_options_gbx_layout.addWidget(self.max_lbl, 0, 2)
        self.gridding_options_gbx_layout.addWidget(self.n_lbl, 0, 3)
        self.gridding_options_gbx_layout.addWidget(self.h_lbl, 1, 0)
        self.gridding_options_gbx_layout.addWidget(self.h_min_txt, 1, 1)
        self.gridding_options_gbx_layout.addWidget(self.h_max_txt, 1, 2)
        self.gridding_options_gbx_layout.addWidget(self.h_n_txt, 1, 3)
        self.gridding_options_gbx_layout.addWidget(self.k_lbl, 2, 0)
        self.gridding_options_gbx_layout.addWidget(self.k_min_txt, 2, 1)
        self.gridding_options_gbx_layout.addWidget(self.k_max_txt, 2, 2)
        self.gridding_options_gbx_layout.addWidget(self.k_n_txt, 2, 3)
        self.gridding_options_gbx_layout.addWidget(self.l_lbl, 3, 0)
        self.gridding_options_gbx_layout.addWidget(self.l_min_txt, 3, 1)
        self.gridding_options_gbx_layout.addWidget(self.l_max_txt, 3, 2)
        self.gridding_options_gbx_layout.addWidget(self.l_n_txt, 3, 3)

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.scan_lstw, 0, 0)
        self.layout.addWidget(self.scan_details_gbx, 1, 0)
        self.layout.setRowStretch(0, 1)
        self.layout.setRowStretch(1, 2)

        # Connections
        self.scan_lstw.itemClicked.connect(self.previewScan)

    # ------------------------------------------------------------------------------

    def loadProjectScanList(self, project):
        """
        Populates scan list.
        """

        self.project = project
        self.scan_lstw.clear()
        self.scan_lstw.addItems(self.project.scan_numbers)

    # ------------------------------------------------------------------------------

    def previewScan(self):
        """
        Displays preview information about a scan.
        """

        i = self.scan_lstw.currentRow()
        scan = self.project.scans[i]

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
        self.h_min_txt.setText(str(round(np.amin(scan.h_map), 3)))
        self.h_max_txt.setText(str(round(np.amax(scan.h_map), 3)))
        self.h_n_txt.setText(str())
        self.k_min_txt.setText(str(round(np.amin(scan.k_map), 3)))
        self.k_max_txt.setText(str(round(np.amax(scan.k_map), 3)))
        self.k_n_txt.setText(str())
        self.l_min_txt.setText(str(round(np.amin(scan.l_map), 3)))
        self.l_max_txt.setText(str(round(np.amax(scan.l_map), 3)))
        self.l_n_txt.setText(str())

        self.scan_details_gbx.setEnabled(True)

    # ------------------------------------------------------------------------------

    def loadScan(self, index):
        """
        Loads scan data into a new DataView widget tab
        """
        
        ...

# ==================================================================================