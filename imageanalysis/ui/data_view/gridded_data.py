"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""

import numpy as np
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea

from imageanalysis.structures import Scan
from imageanalysis.ui.data_view.image_tool import ImageTool


class GriddedDataWidget(DockArea):
    """Allows users to view gridded image data from a scan."""

    def __init__(self, scan: Scan) -> None:
        super(GriddedDataWidget, self).__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        
        self.scan = scan

        # Child widgets
        self.image_tool = ImageTool(parent=self)
        self.controller = GriddedDataController(
            parent=self,
            image_tool=self.image_tool,
            scan=scan
        )

        # Child docks
        self.controller_dock = Dock(
            name="Controller",
            size=(1, 1),
            widget=self.controller,
            hideTitle=True,
            closable=False
        )
        self.image_tool_dock = Dock(
            name="Controller",
            size=(1, 5),
            widget=self.image_tool,
            hideTitle=True,
            closable=False
        )
        # Sets max height for controller
        self.controller_dock.setMaximumHeight(200)

        # Add docks to dock area
        self.addDock(self.controller_dock)
        self.addDock(self.image_tool_dock, "bottom", self.controller_dock)

class GriddedDataController(QtGui.QWidget):
    """Controls dimension order and index of gridded image slice in view."""

    # Signal changing dimension order
    dimensionOrderChanged = QtCore.pyqtSignal()

    def __init__(
        self,
        parent: GriddedDataWidget,
        image_tool: ImageTool,
        scan: Scan
    ) -> None:
        super(GriddedDataController, self).__init__()

        self.parent = parent
        self.image_tool = image_tool
        self.scan = scan
        self.data = scan.gridded_image_data
        self.coords = scan.gridded_image_coords
        self.dim_order = (0, 1, 2)
        self.slice_index = 0

        # For dragging and dropping
        self.setAcceptDrops(True)

        # Child widgets (Dimension controllers)
        self.h_ctrl = GriddedDimensionController(
            parent=self,
            label="H",
            coords=list(self.coords[0])
        )
        self.k_ctrl = GriddedDimensionController(
            parent=self,
            label="K",
            coords=list(self.coords[1])
        )
        self.l_ctrl = GriddedDimensionController(
            parent=self,
            label="L",
            coords=list(self.coords[2])
        )
        self.controllers = [self.h_ctrl, self.k_ctrl, self.l_ctrl]
        self.h_ctrl._setEnabled(enabled=False)
        self.k_ctrl._setEnabled(enabled=False)
        self.l_ctrl._setEnabled(enabled=True)

        # Layout
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.h_ctrl)
        self.layout.addWidget(self.k_ctrl)
        self.layout.addWidget(self.l_ctrl)

        # Connections
        for ctrl in self.controllers:
            ctrl.indexChanged.connect(self._setSliceIndex)
        self.dimensionOrderChanged.connect(self._setDimensionOrder)

        # Set initial image
        self._setImage()

    def _setSliceIndex(self) -> None:
        """Updates index to match index of last dimension controller."""
        self.slice_index = self.layout.itemAt(2).widget().index
        self._setImage()

    def _setDimensionOrder(self) -> None:
        """Updates dimension order to match order of dimension controllers."""

        dim_order = []
        for i in range(self.layout.count()):
            ctrl = self.layout.itemAt(i).widget()
            dim = self.controllers.index(ctrl)
            dim_order.append(dim)
        self.dim_order = tuple(dim_order)
        self._setSliceIndex()

        # Enables/disables dimension controllers based on order
        self.layout.itemAt(0).widget()._setEnabled(False)
        self.layout.itemAt(1).widget()._setEnabled(False)
        self.layout.itemAt(2).widget()._setEnabled(True)

    def _setImage(self) -> None:
        """Loads image in connected image tool."""
        data = np.transpose(self.data, self.dim_order)
        image = data[:, :, self.slice_index]
        x_label = ["H", "K", "L"][self.dim_order[0]]
        y_label = ["H", "K", "L"][self.dim_order[1]]
        x_coords = self.coords[self.dim_order[0]]
        y_coords = self.coords[self.dim_order[1]]

        self.image_tool._setImage(
            image=image,
            data=self.data,
            x_label=x_label,
            y_label=y_label,
            x_coords=x_coords,
            y_coords=y_coords
        )

    def dragEnterEvent(self, e) -> None:
        """For dragging a dimension controller."""
        e.accept()

    def dropEvent(self, e) -> None:
        """For dropping a dimension controller.

        Updates dimension order.
        """

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
        self.dimensionOrderChanged.emit()
        self.dimensionOrderChanged.emit()


class GriddedDimensionController(QtGui.QGroupBox):
    """Child class for DataViewController.

    Three of these are created to control each dimension (H, K, L).
    Houses a slider and combobox to control a single dimension's index.
    """

    # Signal for changing indices
    indexChanged = QtCore.pyqtSignal()

    def __init__(
        self,
        parent: GriddedDataController,
        label: str,
        coords: list
    ) -> None:
        super(GriddedDimensionController, self).__init__()

        self.parent = parent
        self.index = 0
        self.label = label
        self.coords = coords

        # Child widgets
        self.dim_lbl = QtGui.QLabel(label)
        self.dim_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.dim_slider.setMaximum(len(coords) - 1)
        self.dim_cbx = QtGui.QComboBox()
        self.dim_cbx.addItems([str(round(i, 5)) for i in coords])

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dim_lbl, 0, 0)
        self.layout.addWidget(self.dim_slider, 0, 1, 1, 5)
        self.layout.addWidget(self.dim_cbx, 0, 6, 1, 1)

        # Connections
        self.dim_slider.valueChanged.connect(self._setIndex)
        self.dim_cbx.currentIndexChanged.connect(self._setIndex)

    def _setIndex(self) -> None:
        """Sets index value."""

        sender = self.sender()
        index = None
        if sender == self.dim_slider:
            index = sender.value()
            self.dim_cbx.setCurrentIndex(index)
        elif sender == self.dim_cbx:
            index = sender.currentIndex()
            self.dim_slider.setValue(index)
        self.index = index
        self.indexChanged.emit()

    def _setEnabled(self, enabled: bool) -> None:
        """Enables/disables slider and combobox."""

        if enabled:
            self.dim_slider.setEnabled(True)
            self.dim_cbx.setEnabled(True)
        else:
            self.dim_slider.setEnabled(False)
            self.dim_cbx.setEnabled(False)

    def mouseMoveEvent(self, e) -> None:
        """Checks if dimension controller is being dragged."""

        if isinstance(self.parent, GriddedDataController):
            if e.buttons() == QtCore.Qt.LeftButton:
                drag = QtGui.QDrag(self)
                mime = QtCore.QMimeData()
                drag.setMimeData(mime)
                drag.exec_(QtCore.Qt.MoveAction)
