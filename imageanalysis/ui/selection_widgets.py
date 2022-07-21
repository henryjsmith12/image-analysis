"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui

from imageanalysis.io import isValidProjectPath, getSPECPaths, getXMLPaths
from imageanalysis.structures import Project

# ==================================================================================

class ProjectSelectionWidget(QtGui.QWidget):
    """
    Allows users to open a project.
    """

    def __init__(self) -> None:
        super(ProjectSelectionWidget, self).__init__()

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
        self.spec_lbl = QtGui.QLabel("SPEC:")
        self.spec_cbx = QtGui.QComboBox()
        self.instrument_lbl = QtGui.QLabel("Instr. Config.:")
        self.instrument_cbx = QtGui.QComboBox()
        self.detector_lbl = QtGui.QLabel("Det. Config.:")
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
        self.spec_path = self.spec_cbx.currentText()
        self.instrument_path = self.instrument_cbx.currentText()
        self.detector_path = self.detector_cbx.currentText()

        if "" not in [self.spec_path, self.instrument_path, self.detector_path]:
            self.load_project_btn.setEnabled(True)
        else:
            self.load_project_btn.setEnabled(False)

    # ------------------------------------------------------------------------------

    def loadProject(self):

        project = Project(
            project_path=self.project_path,
            spec_path=self.spec_path,
            instrument_path=self.instrument_path,
            detector_path=self.detector_path
        )

# ==================================================================================

class ScanSelectionWidget(QtGui.QWidget):

    def __init__(self) -> None:
        super(ScanSelectionWidget, self).__init__()

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

# ==================================================================================