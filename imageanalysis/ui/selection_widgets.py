"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui

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
        self.project_btn.clicked.connect(self.select_project)

    # ------------------------------------------------------------------------------

    def select_project(self):
        """
        Allows user to select a directory with a file dialog and then validates the 
        selected directory.
        """
        
        project_path = QtGui.QFileDialog.getExistingDirectory(self, "Select Project")
        

# ==================================================================================

class ScanSelectionWidget(QtGui.QWidget):

    def __init__(self) -> None:
        super(ScanSelectionWidget, self).__init__()

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

# ==================================================================================