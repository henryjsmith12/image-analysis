"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""

from ctypes import alignment
import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea

from imageanalysis.ui.data_view.image_tool.color_mapping import \
    ColorMapController


class ImageTool(DockArea):
    """Handles image visualization and manipulation."""

    colorMapUpdated = QtCore.pyqtSignal()
    imageUpdated = QtCore.pyqtSignal()

    def __init__(self, parent) -> None:
        super(ImageTool, self).__init__()

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

        # Child widgets
        self.plot_3d = ImagePlot(parent=self, dock=self.plot_3d_dock, n_dim=3)
        self.plot_2d = ImagePlot(parent=self, dock=self.plot_2d_dock, n_dim=2)
        self.plot_1d = LinePlot(parent=self, dock=self.plot_1d_dock)
        self.controller = ImageToolController(
            parent=self,
            dock=self.controller_dock
        )

        # Adds widgets to docks
        self.plot_3d_dock.addWidget(self.plot_3d)
        self.plot_2d_dock.addWidget(self.plot_2d)
        self.plot_1d_dock.addWidget(self.plot_1d)
        self.controller_dock.addWidget(self.controller)

        # Adds docks to layout
        self.addDock(self.controller_dock)
        self.addDock(self.plot_3d_dock, "left", self.controller_dock)
        self.addDock(self.plot_2d_dock, "bottom", self.plot_3d_dock)
        self.addDock(self.plot_1d_dock, "bottom", self.plot_2d_dock)
        self.controller_dock.setMaximumWidth(220)
        self.controller_dock.setMinimumWidth(220)

        # Hides 2D and 1D plots
        # Will be made visible when an ROI is added
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
        """Sets an image with given parameters to the 3D ImagePlot"""

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

        # For first runthrough
        # Applies a color map to the image
        if self.data is None:
            self.data = data
            self.data_range = (np.amin(data), np.amax(data))
            self.controller._setColorMap()

    def _setColorMap(
        self,
        color_map: pg.ColorMap,
        range: tuple
    ) -> None:
        """Applies a color map and color bar object to the plots."""

        self.color_map = color_map
        self.color_map_range = range

        # For first runthrough
        if self.color_bar_3d is None:
            # Creates color bar for plot
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
        # Applys color map to plot
        self.plot_3d.setColorMap(color_map)
        self.color_bar_3d.setCmap(color_map)
        # Adjusts color map range in color bar
        self.color_bar_3d.setLevels(range)

        if self.plot_2d.isVisible():
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
            self.plot_2d.setColorMap(color_map)
            self.color_bar_2d.setCmap(color_map)
            self.color_bar_2d.setLevels(range)

        self.plot_3d._plot(
            image=self.image,
            x_label=self.x_label,
            y_label=self.y_label,
            x_coords=self.x_coords,
            y_coords=self.y_coords,
        )

        self.colorMapUpdated.emit()


class ImageToolController(QtGui.QWidget):
    """Handles color mapping, mouse info, and ROI's."""

    def __init__(
        self,
        parent: ImageTool,
        dock: Dock
    ) -> None:
        super(ImageToolController, self).__init__()

        self.image_tool = parent
        self.dock = dock

        # Imported here to avoid circular imports
        from imageanalysis.ui.data_view.image_tool.roi import ROIController

        # Scroll area
        self.scroll_area = QtGui.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area_widget = QtGui.QWidget()
        self.scroll_area_layout = QtGui.QVBoxLayout()
        self.scroll_area_widget.setLayout(self.scroll_area_layout)

        # Child widgets
        self.mouse_info_widget = MouseInfoWidget()
        self.color_map_ctrl = ColorMapController(parent=self)
        self.plot_3d_roi_ctrl = ROIController(
            parent_plot=self.image_tool.plot_3d,
            child_plot=self.image_tool.plot_2d,
            image_tool=self.image_tool,
            title="Image Plot #1"
        )
        self.plot_2d_roi_ctrl = ROIController(
            parent_plot=self.image_tool.plot_2d,
            child_plot=self.image_tool.plot_1d,
            image_tool=self.image_tool,
            title="Image Plot #2"
        )
        self.plot_2d_roi_ctrl.hide()

        # Child layout
        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.scroll_area)

        self.scroll_area_layout.addWidget(self.mouse_info_widget)
        self.scroll_area_layout.addWidget(self.color_map_ctrl)
        self.scroll_area_layout.addWidget(self.plot_3d_roi_ctrl)
        self.scroll_area_layout.addWidget(self.plot_2d_roi_ctrl)
        self.scroll_area.setWidget(self.scroll_area_widget)
        self.scroll_area_widget.setFixedWidth(190)

        # Connections
        self.color_map_ctrl.colorMapChanged.connect(self._setColorMap)

    def _setMouseInfo(self, x, y, sender) -> None:

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
                    if sender == self.image_tool.plot_3d:
                        i = self.image_tool.parent.controller.slice_index
                        scan = self.image_tool.parent.scan
                        h, k, l = scan.rsm[i, x, y]
                        value = scan.raw_image_data[i, x, y]
                    elif sender == self.image_tool.plot_2d:
                        h, k, l, value = None, None, None, None
                # GriddedDataWidget
                elif type(self.image_tool.parent) == GriddedDataWidget:
                    if sender == self.image_tool.plot_3d:
                        ctrl = self.image_tool.parent.controller
                        dim_order = ctrl.dim_order
                        data = np.transpose(self.image_tool.data, dim_order)
                        i = ctrl.slice_index
                        value = data[x, y, i]
                        scan = self.image_tool.parent.scan
                        coords = scan.gridded_image_coords
                        h = coords[0][[x, y, i][dim_order.index(0)]]
                        k = coords[1][[x, y, i][dim_order.index(1)]]
                        l = coords[2][[x, y, i][dim_order.index(2)]]
                    elif sender == self.image_tool.plot_2d:
                        h, k, l, value = None, None, None, None
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

    def __init__(self, parent, dock, n_dim) -> None:
        super(ImagePlot, self).__init__(
            imageItem=pg.ImageItem(),
            view=pg.PlotItem()
        )

        # Sets parent widget
        self.image_tool = parent
        self.controller = None
        self.dock = dock
        self.n_dim = n_dim

        # Class variables for plotting
        self.data = None
        self.image_data = None
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
        self.getView().showGrid(x=True, y=True, alpha=0.5)

        # Connections
        self.getView().scene().sigMouseMoved.connect(self._updateMousePoint)

    def _hide(self) -> None:
        """Hides plot and parent dock."""

        self.hide()
        self.dock.hide()

    def _show(self) -> None:
        """Shows plot and parent dock."""

        self.show()
        self.dock.show()

    def _plot(
        self,
        image: np.ndarray=None,
        x_label: str=None,
        y_label: str=None,
        x_coords: np.ndarray=None,
        y_coords: np.ndarray=None,
        x_axis: bool=True,
        y_axis: bool=True
    ) -> None:
        """Normalizes and plots image with proper labels and axes."""

        self.image_data = image
        self.x_label = x_label
        self.y_label = y_label
        self.x_coords = x_coords
        self.y_coords = y_coords

        self._setLabels(x_label, y_label)
        self._setCoordinates(x_coords, y_coords)
        self._normalizeImage()

        self.setImage(
            img=self.norm_image,
            autoRange=False,
            autoLevels=False,
            transform=self.transform
        )
        
        if x_axis:
            self.getView().showAxis("bottom")
        else:
            self.getView().hideAxis("bottom")

        if y_axis:
            self.getView().showAxis("left")
        else:
            self.getView().hideAxis("left")

        self.updated.emit()

    def _normalizeImage(self) -> None:
        """Normalizes image values for color mapping."""

        image = np.copy(self.image_data)
        if self.image_tool.color_map_range is None:
            norm_max = 1
        else:
            norm_max = self.image_tool.color_map_range[-1]
        image[image > norm_max] = norm_max
        image[image == 0] = np.NAN
        image = image / norm_max
        self.norm_image = image

    def _setLabels(self, x_label, y_label) -> None:
        """Sets x and y axis labels."""

        if x_label is not None and type(x_label) == str:
            self.x_label = x_label
            self.getView().setLabel("bottom", x_label)
        if y_label is not None and type(y_label) == str:
            self.y_label = y_label
            self.getView().setLabel("left", y_label)

    def _setCoordinates(self, x_coords, y_coords) -> None:
        """Adjusts image position and scaling."""

        self.transform = QtGui.QTransform()
        if x_coords is not None:
            self.x_coords = x_coords
        else:
            self.x_coords = np.linspace(
                start=0,
                stop=self.image_data.shape[0] - 1,
                num=self.image_data.shape[0],
                endpoint=False
            )

        if y_coords is not None:
            self.y_coords = y_coords
        else:
            self.y_coords = np.linspace(
                start=0,
                stop=self.image_data.shape[1] - 1,
                num=self.image_data.shape[1],
                endpoint=False
            )

        scale = (
            self.x_coords[1] - self.x_coords[0],
            self.y_coords[1] - self.y_coords[0]
        )
        pos = (self.x_coords[0], self.y_coords[0])
        self.transform.translate(*pos)
        self.transform.scale(*scale)

    def _updateMousePoint(self, scene_point=None) -> None:
        """Updates mouse coordinates."""

        if self.controller is None:
            self.controller = self.image_tool.controller

        if scene_point is not None:
            view_point = self.getView().vb.mapSceneToView(scene_point)
            x_point = int(
                self.image_data.shape[0] * (
                    (view_point.x() - self.x_coords[0]) /
                    (self.x_coords[-1] - self.x_coords[0])
                )
            )
            y_point = int(
                self.image_data.shape[1] * (
                    (view_point.y() - self.y_coords[0]) /
                    (self.y_coords[-1] - self.y_coords[0])
                )
            )
            if (
                0 <= x_point < self.image_data.shape[0] and
                0 <= y_point < self.image_data.shape[1]
            ):
                self.controller._setMouseInfo(x_point, y_point, sender=self)
            else:
                self.controller._setMouseInfo(None, None, sender=self)

    def _setCoordinateIntervals(self, coords, labels):
        
        if len(coords) == 3 and len(labels) == 3:
            l1, l2, l3 = labels
            c1, c2, c3 = coords
            
            self.getView().setTitle(f"{l1}: ({round(c1[0], 5)}, {round(c1[-1], 5)})<br>{l2}: ({round(c2[0], 5)}, {round(c2[-1], 5)})<br>{l3}: ({round(c3[0], 5)}, {round(c3[-1], 5)})", justify="right")

            self.intervals = {
                l1: c1, l2: c2, l3: c3
            }

class LinePlot(pg.PlotWidget):
    """Adapted pyqtgraph PlotWidget object"""

    def __init__(self, parent, dock) -> None:
        super().__init__()

        self.image_tool = parent
        self.dock = dock

    def _hide(self) -> None:
        """Hides plot and dock."""

        self.hide()
        self.dock.hide()

    def _show(self) -> None:
        """Shows plot and dock."""

        self.show()
        self.dock.show()

    def _plot(
        self,
        data: np.ndarray=None,
        x_label: str=None,
        y_label: str=None,
        x_coords: np.ndarray=None,
        y_coords: np.ndarray=None,
        x_axis: bool=True,
        y_axis: bool=True
    ) -> None:
        """Plots data points as a line."""

        self.plot(data, clear=True)

        if x_axis:
            self.showAxis("bottom")
        else:
            self.hideAxis("bottom")

        if y_axis:
            self.showAxis("left")
        else:
            self.hideAxis("left")

    def _setCoordinateIntervals(self, coords, labels):
        
        if len(coords) == 3 and len(labels) == 3:
            l1, l2, l3 = labels
            c1, c2, c3 = coords
            
            self.setTitle(f"{l1}: ({round(c1[0], 5)}, {round(c1[-1], 5)})<br>{l2}: ({round(c2[0], 5)}, {round(c2[-1], 5)})<br>{l3}: ({round(c3[0], 5)}, {round(c3[-1], 5)})", justify="right")

            self.intervals = {
                l1: c1, l2: c2, l3: c3
            }

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

        if value is not None:
            self.h_txt.setText(str(round(h, 7)))
            self.k_txt.setText(str(round(k, 7)))
            self.l_txt.setText(str(round(l, 7) or ""))
            self.value_txt.setText(str(round(value, 3)))
        else:
            self.h_txt.setText("")
            self.k_txt.setText("")
            self.l_txt.setText("")
            self.value_txt.setText("")
