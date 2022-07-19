"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui
from pyqtgraph.dockarea import Dock, DockArea

# ==================================================================================

class MainWindow(QtGui.QWidget):
    """
    Main window for application. Houses DockArea that contains child widgets.
    """
    
    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        # Window attributes
        self.setMinimumSize(1400, 800)
        self.setGeometry(0, 50, 1400, 800)
        self.setWindowTitle("image-analysis")

        # Child widgets


        # Docks
        self.dock_area = DockArea()
        self.project_selection_dock = Dock(
            name="Select Project",
            size=(1, 1),
            widget=None,
            hideTitle=True,
            closable=False
        )
        self.scan_selection_dock = Dock(
            name="Select Scan", 
            size=(1, 2), 
            widget=None, 
            hideTitle=True, 
            closable=False
        )
        self.data_view_dock = Dock(
            name="Data View", 
            size=(2, 3), 
            widget=None, 
            hideTitle=True, 
            closable=False
        )
        self.plot_view_dock = Dock(
            name="Plot View", 
            size=(2, 3), 
            widget=None, 
            hideTitle=True, 
            closable=False
        )
        self.dock_area.addDock(self.project_selection_dock)
        self.dock_area.addDock(self.scan_selection_dock, "bottom", self.project_selection_dock)
        self.dock_area.addDock(self.data_view_dock, "right", self.scan_selection_dock)
        self.dock_area.addDock(self.plot_view_dock, "right", self.data_view_dock)
        self.dock_area.moveDock(self.project_selection_dock, "left", self.data_view_dock)
        self.dock_area.moveDock(self.project_selection_dock, "top", self.scan_selection_dock)

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dock_area)

# ==================================================================================