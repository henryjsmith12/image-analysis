"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from pyqtgraph import QtGui
from pyqtgraph.dockarea import Dock, DockArea

from imageanalysis.ui.data_view import DataView
from imageanalysis.ui.plot_view import PlotView
from imageanalysis.ui.selection_widgets import \
    ProjectSelectionWidget, ScanSelectionWidget


class MainWindow(QtGui.QWidget):
    """Main window for application.

    Houses DockArea that contains child widgets.
    """

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        # Window attributes
        self.setMinimumSize(1000, 800)
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle("image-analysis")

        # Child widgets
        self.project_selection_widget = ProjectSelectionWidget(parent=self)
        self.scan_selection_widget = ScanSelectionWidget(parent=self)
        self.data_view = DataView()
        self.plot_view = PlotView()

        # Docks
        self.dock_area = DockArea()
        self.project_selection_dock = Dock(
            name="Select Project",
            size=(1, 1),
            widget=self.project_selection_widget,
            hideTitle=True,
            closable=False
        )
        self.scan_selection_dock = Dock(
            name="Select Scan",
            size=(1, 4),
            widget=self.scan_selection_widget,
            hideTitle=True,
            closable=False
        )
        self.data_view_dock = Dock(
            name="DataView",
            size=(5, 5),
            widget=self.data_view,
            hideTitle=True,
            closable=False
        )
        self.plot_view_dock = Dock(
            name="PlotView",
            size=(5, 5),
            widget=self.plot_view,
            hideTitle=True,
            closable=False
        )

        # Setting maximum size for selection docks
        self.project_selection_dock.setMaximumWidth(300)
        self.scan_selection_dock.setMaximumWidth(300)
        self.data_view_dock.setStretch(5, 5)
        self.plot_view_dock.setStretch(5, 5)

        # Adds docks to dock area
        self.dock_area.addDock(self.project_selection_dock)
        self.dock_area.addDock(
            self.scan_selection_dock,
            "bottom",
            self.project_selection_dock
        )
        self.dock_area.addDock(
            self.data_view_dock,
            "right",
            self.scan_selection_dock
        )
        self.dock_area.moveDock(
            self.project_selection_dock,
            "left",
            self.data_view_dock
        )
        self.dock_area.moveDock(
            self.project_selection_dock,
            "top",
            self.scan_selection_dock
        )

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dock_area)
