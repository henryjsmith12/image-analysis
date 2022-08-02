"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import numpy as np
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea

# ----------------------------------------------------------------------------------

from imageanalysis.ui.data_view.utils import ImageTool

# ==================================================================================

class GriddedDataWidget(DockArea):

    def __init__(self, scan) -> None:
        super(GriddedDataWidget, self).__init__()

        self.scan = scan

        self.image_tool_3d = ImageTool()
        self.image_tool_2d = ImageTool()
        self.controller = GriddedDataController(scan, self.image_tool_3d)
        
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
        self.controller_dock.setMaximumHeight(200)
        self.addDock(self.controller_dock)
        self.addDock(self.image_tool_3d_dock, "bottom" ,self.controller_dock)
        #self.addDock(self.image_tool_2d_dock, "bottom" ,self.image_tool_3d_dock)
        
# ==================================================================================

class GriddedDataController(QtGui.QWidget):

    orderUpdated = QtCore.pyqtSignal()

    def __init__(self, scan, image_tool) -> None:
        super(GriddedDataController, self).__init__()

        self.data = scan.gridded_image_data
        self.dim_order = (0, 1, 2)
        self.image_tool = image_tool
        self.index = None
        self.scan = scan
        h_info = {"label" : "H", "coords" : self.scan.gridded_image_coords[0]}
        k_info = {"label" : "K", "coords" : self.scan.gridded_image_coords[1]}
        l_info = {"label" : "L", "coords" : self.scan.gridded_image_coords[2]}
        self.setAcceptDrops(True)

        # Child widgets
        self.h_controller = GriddedDimensionController(self, h_info)
        self.h_controller.setEnabled(False)
        self.k_controller = GriddedDimensionController(self, k_info)
        self.k_controller.setEnabled(False)
        self.l_controller = GriddedDimensionController(self, l_info)
        self.dimension_controllers = [self.h_controller, self.k_controller, self.l_controller]

        # Layout
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        for dim_ctrl in self.dimension_controllers:
            self.layout.addWidget(dim_ctrl)

        # Connections
        for dim_ctrl in self.dimension_controllers:
            dim_ctrl.updated.connect(self.setIndex)
            dim_ctrl.updated.connect(self.setImage)
        self.orderUpdated.connect(self.setDimensionOrder)
        self.orderUpdated.connect(self.setImage)

    # ------------------------------------------------------------------------------

    def setDimensionOrder(self):
        dim_order = []
        for i in range(self.layout.count()):
            dim_ctrl = self.layout.itemAt(i).widget()
            dim = [self.h_controller, self.k_controller, self.l_controller].index(dim_ctrl)
            dim_order.append(dim)
        self.dim_order = tuple(dim_order)

        self.layout.itemAt(0).widget().setEnabled(False)
        self.layout.itemAt(1).widget().setEnabled(False)
        self.layout.itemAt(2).widget().setEnabled(True)

    # ------------------------------------------------------------------------------

    def setIndex(self):
        sender = self.sender()
        self.index = sender.index

    # ------------------------------------------------------------------------------

    def setImage(self):
        if self.data is None:
            self.data = self.scan.gridded_image_data

        index = self.index
        dim_order = self.dim_order # e.g. (0, 1, 2)
        data = self.data.transpose(*dim_order)
        labels = [x for i, x in sorted(zip(list(dim_order), ["H", "K", "L"]))]
        image = data[:, :, index]

        self.image_tool.setImage(self.data, image, labels[0], labels[1])

    # ------------------------------------------------------------------------------

    def dragEnterEvent(self, e):
        e.accept()

    # ------------------------------------------------------------------------------

    def dropEvent(self, e):
        drop_pos = e.pos()
        widget = e.source()

        for i in range(self.layout.count()):
            w = self.layout.itemAt(i).widget()
            if drop_pos.y() < w.y():
                self.layout.insertWidget(i - 1, widget)
                break
            elif i == self.layout.count() - 1:
                self.layout.insertWidget(i, widget)
                break

        e.accept()
        self.orderUpdated.emit()
    
# ==================================================================================

class GriddedDimensionController(QtGui.QGroupBox):

    updated = QtCore.pyqtSignal()

    def __init__(self, parent, dim_info) -> None:
        super(GriddedDimensionController, self).__init__()

        self.parent = parent
        self.index = 0

        # Child widgets
        self.dim_lbl = QtGui.QLabel(dim_info["label"])
        self.dim_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.dim_slider.setMaximum(len(dim_info["coords"]) - 1)
        self.dim_cbx = QtGui.QComboBox()
        coords = [str(round(i, 5)) for i in dim_info["coords"]]
        self.dim_cbx.addItems(coords)

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dim_lbl, 0, 0)
        self.layout.addWidget(self.dim_slider, 0, 1, 1, 5)
        self.layout.addWidget(self.dim_cbx, 0, 6, 1, 1)
        for i in range(self.layout.columnCount()):
            self.layout.setRowStretch(i, 1)

        # Connections
        self.dim_slider.valueChanged.connect(self.setIndex)
        self.dim_cbx.currentIndexChanged.connect(self.setIndex)

    # ------------------------------------------------------------------------------

    def setIndex(self):
        sender = self.sender()
        index = None
        if sender == self.dim_slider:
            index = sender.value()
            self.dim_cbx.setCurrentIndex(index)
        elif sender == self.dim_cbx:
            index = sender.currentIndex()
            self.dim_slider.setValue(index)
        self.index = index
        self.updated.emit()

    # ------------------------------------------------------------------------------
    
    def mouseMoveEvent(self, e):
        if isinstance(self.parent, GriddedDataController):
            if e.buttons() == QtCore.Qt.LeftButton:
                drag = QtGui.QDrag(self)
                mime = QtCore.QMimeData()
                drag.setMimeData(mime)
                drag.exec_(QtCore.Qt.MoveAction)

# ==================================================================================