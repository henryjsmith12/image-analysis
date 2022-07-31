"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from matplotlib.colors import LogNorm, Normalize
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea

# ----------------------------------------------------------------------------------

from imageanalysis.ui.data_view.utils import ImageTool

# ==================================================================================

class RawDataWidget(DockArea):

    def __init__(self, scan) -> None:
        super(RawDataWidget, self).__init__()

        self.scan = scan

        self.controller = RawDataController()
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
        self.controller_dock.setMaximumHeight(75)
        self.addDock(self.controller_dock)
        self.addDock(self.image_tool_3d_dock, "bottom" ,self.controller_dock)
        self.addDock(self.image_tool_2d_dock, "bottom" ,self.image_tool_3d_dock)

        data = self.scan.raw_image_data.astype("int64")
        self.image_tool_3d.image_view.setImage(data)

        stop_count = 15
        cmap_stops = np.logspace(0.0, float(len(str(np.amax(data)))), num=stop_count) / (10 ** len(str(np.amax(data))))
        cmap_colors = pg.getFromMatplotlib("jet").getLookupTable(nPts=stop_count)

        # color map
        cmap = pg.ColorMap(cmap_stops, cmap_colors)
        self.image_tool_3d.image_view.setColorMap(cmap)

# ==================================================================================

class RawDataController(QtGui.QWidget):

    def __init__(self) -> None:
        super(RawDataController, self).__init__()

        self.data_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.data_sbx = QtGui.QSpinBox()
        self.data_type_rbg = QtGui.QButtonGroup()
        self.h_rbtn = QtGui.QRadioButton("H")
        self.k_rbtn = QtGui.QRadioButton("K")
        self.l_rbtn = QtGui.QRadioButton("L")
        self.intensity_rbtn = QtGui.QRadioButton("Intensity")
        for btn in [self.h_rbtn, self.k_rbtn, self.l_rbtn, self.intensity_rbtn]:
            self.data_type_rbg.addButton(btn)

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.data_slider, 0, 0, 1, 3)
        self.layout.addWidget(self.data_sbx, 0, 3, 1, 1)
        self.layout.addWidget(self.h_rbtn, 1, 0, 1, 1)
        self.layout.addWidget(self.k_rbtn, 1, 1, 1, 1)
        self.layout.addWidget(self.l_rbtn, 1, 2, 1, 1)
        self.layout.addWidget(self.intensity_rbtn, 1, 3, 1, 1)
        for i in range(self.layout.rowCount()):
            self.layout.setRowStretch(i, 1)
        for i in range(self.layout.columnCount()):
            self.layout.setRowStretch(i, 1)

# ==================================================================================