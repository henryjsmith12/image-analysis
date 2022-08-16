"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea
from imageanalysis.structures import Scan

from imageanalysis.ui.data_view.utils import ImageTool


class GriddedDataWidget(DockArea):
    """Allows users to view gridded image data from a scan."""

    def __init__(self, scan: Scan) -> None:
        super(GriddedDataWidget, self).__init__()

        self.scan = scan

        # Child widgets
        self.image_tool_3d = ImageTool()
        self.image_tool_2d = ImageTool()
        self.controller = GriddedDataController(scan, self.image_tool_3d)

        # Child docks
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
        # Sets max height for controller
        self.controller_dock.setMaximumHeight(200)

        # Add docks to dock area
        self.addDock(self.controller_dock)
        self.addDock(self.image_tool_3d_dock, "bottom", self.controller_dock)


# TODO: Reorganize way HKL info is passed down
class GriddedDataController(QtGui.QWidget):
    """Controls dimension order and index of gridded image slice in view."""

    # Signal to update dimension order
    orderUpdated = QtCore.pyqtSignal()

    def __init__(
        self,
        scan: Scan,
        image_tool: ImageTool
    ) -> None:
        super(GriddedDataController, self).__init__()

        self.data = scan.gridded_image_data
        self.coords = scan.gridded_image_coords
        self.image_tool = image_tool
        self.scan = scan
        self.dim_order = (0, 1, 2)
        self.index = 0

        # Info for each dimension
        h_info = {"label": "H", "coords": self.scan.gridded_image_coords[0]}
        k_info = {"label": "K", "coords": self.scan.gridded_image_coords[1]}
        l_info = {"label": "L", "coords": self.scan.gridded_image_coords[2]}

        # For dragging and dropping
        self.setAcceptDrops(True)

        # Child widgets
        self.h_controller = GriddedDimensionController(self, h_info)
        self.h_controller.dim_slider.setEnabled(False)
        self.h_controller.dim_cbx.setEnabled(False)
        self.k_controller = GriddedDimensionController(self, k_info)
        self.k_controller.dim_slider.setEnabled(False)
        self.k_controller.dim_cbx.setEnabled(False)
        self.l_controller = GriddedDimensionController(self, l_info)
        self.dimension_controllers = [
            self.h_controller,
            self.k_controller,
            self.l_controller
        ]

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

        # Set initial image
        self.setImage()

    def setDimensionOrder(self) -> None:
        """Updates dimension order to match order of dimension controllers."""

        dim_order = []

        for i in range(self.layout.count()):
            dim_ctrl = self.layout.itemAt(i).widget()
            dim = self.dimension_controllers.index(dim_ctrl)
            dim_order.append(dim)
        self.dim_order = tuple(dim_order)
        self.index = self.layout.itemAt(2).widget().index

        # Enables/disables dimension controllers based on order
        self.layout.itemAt(0).widget().dim_slider.setEnabled(False)
        self.layout.itemAt(0).widget().dim_cbx.setEnabled(False)
        self.layout.itemAt(1).widget().dim_slider.setEnabled(False)
        self.layout.itemAt(1).widget().dim_cbx.setEnabled(False)
        self.layout.itemAt(2).widget().dim_slider.setEnabled(True)
        self.layout.itemAt(2).widget().dim_cbx.setEnabled(True)

    def setIndex(self) -> None:
        """Updates index to match index of last dimension controller."""
        self.index = self.layout.itemAt(2).widget().index

    def setImage(self) -> None:
        """Sets image for connected ImageTool."""

        if self.data is None:
            self.data = self.scan.gridded_image_data
            self.coords = self.scan.gridded_image_coords

        # Determines slice direction and index for image
        index = self.index
        dim_order = self.dim_order
        if dim_order[2] == 0:
            image = self.data[index, :, :]
            if dim_order[0] == 2:
                image = image.T
        elif dim_order[2] == 1:
            image = self.data[:, index, :]
            if dim_order[0] == 2:
                image = image.T
        else:
            image = self.data[:, :, index]
            if dim_order[0] == 1:
                image = image.T

        # Determines labels for image
        labels = ["H", "K", "L"]
        x_label = labels[dim_order[0]]
        y_label = labels[dim_order[1]]
        slice_label = labels[dim_order[2]]

        # Determines axis coordinates and slice direction coordinate
        x_coords = self.coords[dim_order[2]]
        y_coords = self.coords[dim_order[2]]
        slice_coord = round(float(self.coords[dim_order[2]][index]), 5)

        self.image_tool.setImage(
            data=self.data,
            image=image,
            x_label=x_label,
            y_label=y_label,
            slice_label=slice_label,
            x_coords=x_coords,
            y_coords=y_coords,
            slice_coord=slice_coord
        )

    def dragEnterEvent(self, e):
        """For dragging a dimension controller."""
        e.accept()

    def dropEvent(self, e):
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
        self.orderUpdated.emit()


class GriddedDimensionController(QtGui.QGroupBox):
    """Houses a slider and combobox to controller a dimensions's index."""

    # Signal to update dimension order index
    updated = QtCore.pyqtSignal()

    def __init__(
        self,
        parent: GriddedDataController,
        dim_info: dict
    ) -> None:
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

    def setIndex(self):
        """Sets order index for dimension."""

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

    def mouseMoveEvent(self, e):
        """For draging/dropping"""

        if isinstance(self.parent, GriddedDataController):
            if e.buttons() == QtCore.Qt.LeftButton:
                drag = QtGui.QDrag(self)
                mime = QtCore.QMimeData()
                drag.setMimeData(mime)
                drag.exec_(QtCore.Qt.MoveAction)
