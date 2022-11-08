"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from PyQt5 import QtWidgets
from pyqtgraph import QtCore
from pyqtgraph.dockarea import Dock, DockArea

from imageanalysis.structures import Scan
from imageanalysis.ui.data_view.image_tool import ImageTool


class RawDataWidget(DockArea):
    """Allows users to view raw image data from a scan."""

    def __init__(self, scan: Scan, parent=None) -> None:
        super(RawDataWidget, self).__init__()
        self.parent = parent

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.scan = scan

        # Child widgets
        self.image_tool = ImageTool(parent=self)
        self.controller = RawDataController(
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
            name="Image Tool",
            size=(1, 10),
            widget=self.image_tool,
            hideTitle=True,
            closable=False
        )
        self.controller_dock.setMaximumHeight(75)
        self.addDock(self.controller_dock)
        self.addDock(self.image_tool_dock, "bottom", self.controller_dock)


class RawDataController(QtWidgets.QWidget):
    """Controls slice index for image in view."""

    def __init__(
        self,
        parent: RawDataWidget,
        image_tool: ImageTool,
        scan: Scan
    ) -> None:
        super(RawDataController, self).__init__()

        self.parent = parent
        self.image_tool = image_tool
        self.scan = scan

        self.data = scan.raw_image_data
        self.slice_index = 0

        # Child widgets
        self.data_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.data_slider.setMaximum(self.data.shape[0] - 1)
        self.data_sbx = QtWidgets.QSpinBox()
        self.data_sbx.setMaximum(self.data.shape[0] - 1)

        # Layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.data_slider, 0, 0, 1, 3)
        self.layout.addWidget(self.data_sbx, 0, 3, 1, 1)
        for i in range(self.layout.columnCount()):
            self.layout.setColumnStretch(i, 1)

        # Connections
        self.data_slider.valueChanged.connect(self._setSliceIndex)
        self.data_sbx.valueChanged.connect(self._setSliceIndex)

        # Display first image
        self._setImage()

    def _setSliceIndex(self) -> None:
        """Sets index for slice in view."""

        sender = self.sender()
        index = sender.value()
        if sender == self.data_slider:
            self.data_sbx.setValue(index)
        elif sender == self.data_sbx:
            self.data_slider.setValue(index)

        self.slice_index = index
        self._setImage()

    def _setImage(self) -> None:
        """Sets image for connected ImageTool."""

        image = self.data[self.slice_index]
        self.image_tool._setImage(
            image=image,
            data=self.data
        )
