"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from matplotlib.colors import LogNorm
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui
from pyqtgraph.dockarea import Dock, DockArea

# ----------------------------------------------------------------------------------

from imageanalysis.ui.data_view.utils import ImageTool

# ==================================================================================

class GriddedDataWidget(DockArea):

    def __init__(self, scan) -> None:
        super(GriddedDataWidget, self).__init__()

        self.scan = scan

        self.controller = GriddedDataController()
        self.image_tool_3d = ImageTool()
        self.image_tool_2d = ImageTool()

        self.controller_dock = Dock(
            name="Controller",
            size=(1, 1),
            widget=self.controller,
            hideTitle=True,
            closable=False
        )
        self.image_tool_3d_dock = Dock(
            name="Controller",
            size=(1, 5),
            widget=self.image_tool_3d,
            hideTitle=True,
            closable=False
        )
        self.image_tool_2d_dock = Dock(
            name="Controller",
            size=(1, 5),
            widget=self.image_tool_2d,
            hideTitle=True,
            closable=False
        )
        self.controller_dock.setMaximumHeight(125)
        self.addDock(self.controller_dock)
        self.addDock(self.image_tool_3d_dock, "bottom" ,self.controller_dock)
        self.addDock(self.image_tool_2d_dock, "bottom" ,self.image_tool_3d_dock)
        
# ==================================================================================

class GriddedDataController(QtGui.QWidget):

    def __init__(self) -> None:
        super(GriddedDataController, self).__init__()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

# ==================================================================================