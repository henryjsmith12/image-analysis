"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""

import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea

from imageanalysis.ui.data_view.image_tool.color_mapping import \
    ColorMapController


class ImageTool(DockArea):
    """Handles image visualization and manipulation."""

    def __init__(self, parent) -> None:
        super().__init__()

        self.parent = parent
        self.data = None
        self.data_range = None
        self.color_map = None
        self.color_bar_3d = None
        self.color_bar_2d = None
        self.color_map_range = None

        # Child docks
        self.plot_3d_dock = Dock(
            name="3D Image Plot",
            size=(10, 10),
            widget=None,
            hideTitle=True,
            closable=False
        )
        self.plot_2d_dock = Dock(
            name="2D Image Plot",
            size=(10, 10),
            widget=None,
            hideTitle=True,
            closable=False
        )
        self.plot_1d_dock = Dock(
            name="Line Plot",
            size=(10, 10),
            widget=None,
            hideTitle=True,
            closable=False
        )
        self.controller_dock = Dock(
            name="Color Mapping",
            size=(10, 1),
            widget=None,
            hideTitle=True,
            closable=False
        )

        self.plot_3d = ImagePlot(parent=self, dock=self.plot_3d_dock)
        self.plot_2d = ImagePlot(parent=self, dock=self.plot_2d_dock)
        self.plot_1d = LinePlot(parent=self, dock=self.plot_1d_dock)
        self.controller = ImageToolController(parent=self, dock=self.controller_dock)
        
        self.plot_3d_dock.addWidget(self.plot_3d)
        self.plot_2d_dock.addWidget(self.plot_2d)
        self.plot_1d_dock.addWidget(self.plot_1d)
        self.controller_dock.addWidget(self.controller)

        # Adds docks to layout
        self.addDock(self.controller_dock)
        self.addDock(self.plot_3d_dock, "left", self.controller_dock)
        self.addDock(self.plot_2d_dock, "bottom", self.plot_3d_dock)
        self.addDock(self.plot_1d_dock, "bottom", self.plot_2d_dock)
        self.controller_dock.setMaximumWidth(200)
        self.controller_dock.setMinimumWidth(200)

        self.plot_2d._hide()
        self.plot_1d._hide()

    def _setImage(
        self,
        data: np.ndarray,
        image: np.ndarray,
        x_label: str=None,
        y_label: str=None,
        x_coords: list=None,
        y_coords: list=None
    ) -> None:

        # For first runthrough
        if self.data is None:
            self.data = data
            self.data_range = (np.amin(data), np.amax(data))

        self.image = image
        self.x_label = x_label
        self.y_label = y_label
        self.x_coords = x_coords
        self.y_coords = y_coords

        self.plot_3d._plot(
            image=self.image,
            x_label=self.x_label,
            y_label=self.y_label,
            x_coords=self.x_coords,
            y_coords=self.y_coords,
        )
        self.controller._setColorMap()
        
    def _setColorMap(self, color_map, range) -> None:
        """Applies a color map and color bar object to the plots."""
        self.color_map = color_map
        self.color_map_range = range

        self.plot_3d.setColorMap(color_map)
        if self.color_bar_3d is None:
            self.color_bar_3d = pg.ColorBarItem(
                values=range,
                cmap=color_map,
                interactive=False,
                width=15,
                orientation="h"
            )
            self.color_bar_3d.setImageItem(
                img=self.plot_3d.image,
                insert_in=self.plot_3d.getView()
            )
        else:
            self.color_bar_3d.setCmap(color_map)
            self.color_bar_3d.setLevels(range)

        if self.plot_2d.isVisible():
            self.plot_2d.setColorMap(color_map)
            if self.color_bar_2d is None:
                self.color_bar_2d = pg.ColorBarItem(
                    values=range,
                    cmap=color_map,
                    interactive=False,
                    width=15,
                    orientation="h"
                )
                self.color_bar_2d.setImageItem(
                    img=self.plot_2d.image,
                    insert_in=self.plot_2d.getView()
                )
            else:
                self.color_bar_2d.setCmap(color_map)
                self.color_bar_2d.setLevels(range)

        self.plot_3d._plot(
            image=self.image,
            x_label=self.x_label,
            y_label=self.y_label,
            x_coords=self.x_coords,
            y_coords=self.y_coords,
        )

class ImageToolController(QtGui.QWidget):
    """Handles color mapping, mouse info, and ROI's."""

    def __init__(self, parent, dock) -> None:
        super(ImageToolController, self).__init__()

        self.image_tool = parent
        self.dock = dock

        from imageanalysis.ui.data_view.image_tool.roi import ROIController
        # Child widgets
        self.mouse_info_widget = MouseInfoWidget()
        self.color_map_ctrl = ColorMapController(parent=self)
        self.plot_3d_roi_ctrl = ROIController(parent=self.image_tool.plot_3d, child=self.image_tool.plot_2d, title="Image Plot #1")
        self.plot_2d_roi_ctrl = ROIController(parent=self.image_tool.plot_2d, child=self.image_tool.plot_1d, title="Image Plot #2")
        self.plot_2d_roi_ctrl.hide()

        # Child layout
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.mouse_info_widget)
        self.layout.addWidget(self.color_map_ctrl)
        self.layout.addWidget(self.plot_3d_roi_ctrl)
        self.layout.addWidget(self.plot_2d_roi_ctrl)

        # Connections
        self.color_map_ctrl.colorMapChanged.connect(self._setColorMap)

    def _setMouseInfo(self, x, y) -> None:

        if x is None or y is None:
            self.mouse_info_widget._setMouseInfo(None, None, None, None)
        else:
            from imageanalysis.ui.data_view.gridded_data import \
            GriddedDataWidget
            from imageanalysis.ui.data_view.raw_data import \
                RawDataWidget

            h, k, l, value = None, None, None, None

            try:
                # RawDataWidget
                if type(self.image_tool.parent) == RawDataWidget:
                    i = self.image_tool.parent.controller.slice_index
                    h, k, l = self.image_tool.parent.scan.rsm[i, x, y]
                    value = self.image_tool.parent.scan.raw_image_data[i, x, y]
                # GriddedDataWidget
                elif type(self.image_tool.parent) == GriddedDataWidget:
                    dim_order = self.image_tool.parent.controller.dim_order
                    data = np.transpose(self.image_tool.data, dim_order)
                    i = self.image_tool.parent.controller.slice_index
                    value = data[x, y, i]
                    coords = self.image_tool.parent.scan.gridded_image_coords
                    h = coords[0][[x, y, i][dim_order.index(0)]]
                    k = coords[1][[x, y, i][dim_order.index(1)]]
                    l = coords[2][[x, y, i][dim_order.index(2)]]
            except: 
                pass

            # HKL and intensity information passed to ImageToolController
            self.mouse_info_widget._setMouseInfo(h=h, k=k, l=l, value=value)

    def _setColorMap(self) -> None:
        """Applies color map from ColorMapController to ImageTool."""

        self.image_tool._setColorMap(
            color_map=self.color_map_ctrl.color_map,
            range=(0, self.color_map_ctrl.color_map_max)
        )

class ImagePlot(pg.ImageView):
    """An adapted pyqtgraph ImageView object."""

    updated = QtCore.pyqtSignal()

    def __init__(self, parent, dock) -> None:
        super(ImagePlot, self).__init__(
            imageItem=pg.ImageItem(),
            view=pg.PlotItem()
        )

        # Sets parent widget
        self.image_tool = parent
        self.controller = None
        self.dock = dock

        # Class variables for plotting
        self.data = None
        self.image = None
        self.norm_image = None
        self.x_label, self.y_label = None, None
        self.x_coords, self.y_coords = None, None
        self.transform = None
        
        # Removing UI clutter
        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()
        self.getView().setAspectLocked(False)
        self.getView().ctrlMenu = None

        # Connections
        self.getView().scene().sigMouseMoved.connect(self._updateMousePoint)

    def _hide(self):
        self.hide()
        self.dock.hide()

    def _show(self):
        self.show()
        self.dock.show()

    def _plot(
        self,
        image: np.ndarray=None,
        x_label: str=None,
        y_label: str=None,
        x_coords: np.ndarray=None,
        y_coords: np.ndarray=None
    ) -> None:

        self.image = image

        self._setLabels(x_label, y_label)
        self._setCoordinates(x_coords, y_coords)
        self._normalizeImage()
        self.setImage(
            img=self.norm_image,
            autoRange=False,
            autoLevels=False,
            transform=self.transform
        )

        self.updated.emit()

    def _normalizeImage(self) -> None:

        image = np.copy(self.image)
        if self.image_tool.color_map_range is None:
            norm_max = 1
        else:
            norm_max = self.image_tool.color_map_range[-1]
        image[image > norm_max] = norm_max
        image = image / norm_max
        self.norm_image = image

    def _setLabels(self, x_label, y_label):

        if x_label is not None and type(x_label) == str:
            self.x_label = x_label
            self.getView().setLabel("bottom", x_label)
        if y_label is not None and type(y_label) == str:
            self.y_label = y_label
            self.getView().setLabel("left", y_label)

    def _setCoordinates(self, x_coords, y_coords):
        
        self.transform = QtGui.QTransform()
        if x_coords is not None:
            self.x_coords = x_coords
        else:
            self.x_coords = np.linspace(
                start=0,
                stop=self.image.shape[0] - 1,
                num=self.image.shape[0],
                endpoint=False
            )

        if y_coords is not None:
            self.y_coords = y_coords
        else:
            self.y_coords = np.linspace(
                start=0,
                stop=self.image.shape[1] - 1,
                num=self.image.shape[1],
                endpoint=False
            )

        scale = (
            self.x_coords[1] - self.x_coords[0], 
            self.y_coords[1] - self.y_coords[0]
        )
        pos = (self.x_coords[0], self.y_coords[0])
        self.transform.translate(*pos)
        self.transform.scale(*scale)

    def _updateMousePoint(self, scene_point=None):

        if self.controller is None:
            self.controller = self.image_tool.controller

        if scene_point is not None:
            view_point = self.getView().vb.mapSceneToView(scene_point)
            x_point = int(
                self.image.shape[0] * (
                    (view_point.x() - self.x_coords[0]) /
                    (self.x_coords[-1] - self.x_coords[0])
                )
            )
            y_point = int(
                self.image.shape[1] * (
                    (view_point.y() - self.y_coords[0]) /
                    (self.y_coords[-1] - self.y_coords[0])
                )
            )
            if 0 <= x_point < self.image.shape[0] and \
            0 <= y_point < self.image.shape[1]:
                self.controller._setMouseInfo(x_point, y_point)
            else:
                self.controller._setMouseInfo(None, None)

class LinePlot(pg.PlotWidget):
    """Adapted pyqtgraph PlotWidget object"""

    def __init__(self, parent, dock) -> None:
        super().__init__()

        self.image_tool = parent
        self.dock = dock

    def _hide(self):
        self.hide()
        self.dock.hide()

    def _show(self):
        self.show()
        self.dock.show()

class MouseInfoWidget(QtGui.QGroupBox):
    """Handles displaying proper mouse location and associated values."""

    def __init__(self) -> None:
        super().__init__()

        # Child widgets
        self.h_lbl, self.h_txt = QtGui.QLabel("H: "), QtGui.QLineEdit()
        self.h_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.k_lbl, self.k_txt = QtGui.QLabel("K: "), QtGui.QLineEdit()
        self.k_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.l_lbl, self.l_txt = QtGui.QLabel("L: "), QtGui.QLineEdit()
        self.l_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.value_lbl = QtGui.QLabel("Value: ")
        self.value_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.value_txt = QtGui.QLineEdit()

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.h_lbl, 0, 0)
        self.layout.addWidget(self.h_txt, 0, 1, 1, 5)
        self.layout.addWidget(self.k_lbl, 1, 0)
        self.layout.addWidget(self.k_txt, 1, 1, 1, 5)
        self.layout.addWidget(self.l_lbl, 2, 0)
        self.layout.addWidget(self.l_txt, 2, 1, 1, 5)
        self.layout.addWidget(self.value_lbl, 3, 0)
        self.layout.addWidget(self.value_txt, 3, 1, 1, 5)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnStretch(4, 1)
        self.layout.setColumnStretch(5, 1)

    def _setMouseInfo(self, h=None, k=None, l=None, value=None) -> None:
        """Sets values to respective textboxes."""

        if h is not None:
            self.h_txt.setText(str(round(h, 7)))
            self.k_txt.setText(str(round(k, 7)))
            self.l_txt.setText(str(round(l, 7) or ""))
            self.value_txt.setText(str(round(value, 3)))
        else:
            self.h_txt.setText("")
            self.k_txt.setText("")
            self.l_txt.setText("")
            self.value_txt.setText("")
