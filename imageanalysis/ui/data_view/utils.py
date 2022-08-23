"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea
from sklearn import preprocessing


class ImageTool(QtGui.QWidget):
    """Allows user to view and manipulate images."""

    def __init__(self) -> None:
        super(ImageTool, self).__init__()

        self.data, self.image = None, None
        self.data_min, self.data_max = None, None

        self.color_map, self.color_bar = None, None

        self.image_view = ImageView()
        self.color_map_widget = ColorMapWidget(parent=self)

        # Docks
        self.dock_area = DockArea()
        self.image_view_dock = Dock(
            name="Image",
            size=(1, 10),
            widget=self.image_view,
            hideTitle=True,
            closable=False
        )
        self.color_map_dock = Dock(
            name="Color Mapping",
            size=(1, 1),
            widget=self.color_map_widget,
            hideTitle=True,
            closable=False
        )
        self.dock_area.addDock(self.color_map_dock)
        self.dock_area.addDock(
            self.image_view_dock, "top", self.color_map_dock
        )

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dock_area, 0, 0)

        # Connections
        self.color_map_widget.colorMapChanged.connect(self._setColorMap)

    def _setImage(
        self,
        image: np.ndarray,
        data: np.ndarray,
        x_label: str=None,
        y_label: str=None,
        x_coords: list=None,
        y_coords: list=None,
        slice_label: str=None,
        slice_coord: float=None
    ):
        self.image = image

        # First-time runthough
        if self.data is None:
            self.data = data
            self.data_min, self.data_max = np.amin(data), np.amax(data)
            self._setColorMap()

        if x_label is not None:
            self.image_view.getView().setLabel("bottom", x_label)
        if y_label is not None:
            self.image_view.getView().setLabel("left", y_label)

        tr = QtGui.QTransform()
        if x_coords is not None and y_coords is not None:
            scale = (x_coords[1] - x_coords[0], y_coords[1] - y_coords[0])
            pos = (x_coords[0], y_coords[0])
            tr.translate(*pos)
            tr.scale(*scale)

        # Sets slice label and slice coordinate if given
        if slice_label is not None and slice_coord is not None:
            self.image_view.getView().setTitle(f"{slice_label}={slice_coord}")

        # Sets image to ImageView
        self.image_view.setImage(
            image,
            autoRange=False,
            autoLevels=False,
            transform=tr
        )

    def _setColorMap(self):
        """Sets color map and color bar for image."""

        name = self.color_map_widget.name
        scale = self.color_map_widget.scale
        min = np.amin(self.data)
        max = np.amax(self.data)
        n_pts = 16
        base = self.color_map_widget.base
        gamma = self.color_map_widget.gamma

        del self.color_map
        self.color_map = createColorMap(
            name=name,
            scale=scale,
            min=min,
            max=max,
            n_pts=n_pts,
            base=base,
            gamma=gamma
        )
        self.image_view.setColorMap(self.color_map)

        self.color_bar = pg.ColorBarItem(
            values=(min, max),
            cmap=self.color_map,
            interactive=False,
            width=15,
            orientation="h"
        )
        self.color_bar.setImageItem(
            img=self.image,
            insert_in=self.image_view.getView()
        )


class ImageView(pg.ImageView):
    """Altered pyqtgraph ImageView widget."""

    def __init__(self) -> None:
        super(ImageView, self).__init__(
            imageItem=pg.ImageItem(),
            view=pg.PlotItem()
        )
        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()
        self.getView().setAspectLocked(False)
        self.getView().ctrlMenu = None


class ColorMapWidget(QtGui.QWidget):
    """Allows user to apply a colormap to an image."""

    colorMapChanged = QtCore.pyqtSignal()

    def __init__(
        self,
        parent: ImageTool
    ) -> None:
        super(ColorMapWidget, self).__init__()

        self.parent = parent

        available_color_maps = [
            'magma', 'inferno', 'plasma', 'viridis', 'cividis', 'twilight',
            'turbo', 'cool', 'coolwarm', 'afmhot', 'autumn', 'copper',
            'cubehelix', 'gnuplot', 'gnuplot2', 'gray', 'hot', 'hsv', 'jet',
            'nipy_spectral', 'ocean', 'pink', 'prism', 'rainbow',
            'spring', 'summer', 'winter'
        ]
        available_color_maps = sorted(available_color_maps)
        scales = ["linear", "log", "power"]

        self.name = available_color_maps[0]
        self.scale = scales[0]
        self.n_pts = 16
        self.base = 2.0
        self.gamma = 2.0

        # Child widgets
        self.name_cbx = QtGui.QComboBox()
        self.name_cbx.addItems(available_color_maps)
        self.scale_cbx = QtGui.QComboBox()
        self.scale_cbx.addItems(scales)
        self.n_pts_lbl = QtGui.QLabel("# Points:")
        self.n_pts_sbx = QtGui.QSpinBox()
        self.n_pts_sbx.setMinimum(2)
        self.n_pts_sbx.setMaximum(256)
        self.n_pts_sbx.setValue(16)
        self.base_lbl = QtGui.QLabel("Base:")
        self.base_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.base_lbl.hide()
        self.base_sbx = QtGui.QDoubleSpinBox()
        self.base_sbx.setMinimum(0.0001)
        self.base_sbx.setMaximum(1000)
        self.base_sbx.setSingleStep(0.1)
        self.base_sbx.hide()
        self.base_sbx.setValue(2.0)
        self.gamma_lbl = QtGui.QLabel("Gamma:")
        self.gamma_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.gamma_lbl.hide()
        self.gamma_sbx = QtGui.QDoubleSpinBox()
        self.gamma_sbx.setMinimum(0.0001)
        self.gamma_sbx.setMaximum(1000)
        self.gamma_sbx.setSingleStep(0.1)
        self.gamma_sbx.hide()
        self.gamma_sbx.setValue(2.0)

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.name_cbx, 0, 0, 1, 2)
        self.layout.addWidget(self.scale_cbx, 0, 2, 1, 2)
        self.layout.addWidget(self.base_lbl, 0, 4)
        self.layout.addWidget(self.base_sbx, 0, 5)
        self.layout.addWidget(self.gamma_lbl, 0, 4)
        self.layout.addWidget(self.gamma_sbx, 0, 5)

        # Connections
        self.name_cbx.currentIndexChanged.connect(self._setColorMap)
        self.scale_cbx.currentIndexChanged.connect(self._setColorMap)
        self.scale_cbx.currentIndexChanged.connect(self._toggleScaleOptions)
        self.n_pts_sbx.valueChanged.connect(self._setColorMap)
        self.base_sbx.valueChanged.connect(self._setColorMap)
        self.gamma_sbx.valueChanged.connect(self._setColorMap)

    def _setColorMap(self):
        """Sets parameters for color map creation and emits signal."""

        self.name = self.name_cbx.currentText()
        self.scale = self.scale_cbx.currentText()
        self.n_pts = self.n_pts_sbx.value()
        self.base = self.base_sbx.value()
        self.gamma = self.gamma_sbx.value()
        self.colorMapChanged.emit()

    def _toggleScaleOptions(self):
        """Hides/shows respective options for each color map scale."""

        if self.scale_cbx.currentText() == "linear":
            self.base_lbl.hide()
            self.base_sbx.hide()
            self.gamma_lbl.hide()
            self.gamma_sbx.hide()
        elif self.scale_cbx.currentText() == "log":
            self.base_lbl.show()
            self.base_sbx.show()
            self.gamma_lbl.hide()
            self.gamma_sbx.hide()
        elif self.scale_cbx.currentText() == "power":
            self.base_lbl.hide()
            self.base_sbx.hide()
            self.gamma_lbl.show()
            self.gamma_sbx.show()


def createColorMap(
    name: str,
    scale: str,
    min: float=0.0,
    max: float=1.0,
    n_pts: int=16,
    base: float=1.75,
    gamma: float=2
) -> pg.ColorMap:
    """Returns a color map object created from given parameters."""

    if name in pg.colormap.listMaps(source="matplotlib"):
        colors = pg.getFromMatplotlib(name).getLookupTable(nPts=n_pts)
    elif name in pg.colormap.listMaps(source="colorcet"):
        colors = pg.getFromColorcet(name).getLookupTable(nPts=n_pts)
    elif name in pg.colormap.listMaps():
        colors = pg.get(name).getLookupTable(nPts=n_pts)
    else:
        raise KeyError("Color map name not found.")

    if scale == "linear":
        stops = np.linspace(start=min, stop=max, num=n_pts)
        stops = np.array([list(stops)])
        stops = preprocessing.normalize(stops, norm="max")
        stops = list(stops[0])
    elif scale == "log":
        stops = np.logspace(
            start=0,
            stop=7.5,
            endpoint=True,
            num=n_pts,
            base=base
        )
        stops = np.array([list(stops)])
        stops = preprocessing.normalize(stops, norm="max")
        stops = list(stops[0])
    elif scale == "power":
        stops = np.linspace(start=min, stop=max, num=n_pts)
        stops -= min
        stops[stops < 0] = 0
        np.power(stops, gamma, stops)
        stops /= (max - min) ** gamma
        stops = np.array([list(stops)])
        stops = preprocessing.normalize(stops, norm="max")
        stops = list(stops[0])
    else:
        raise ValueError("Scale type not valid.")

    return pg.ColorMap(pos=stops, color=colors)
