"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from sklearn import preprocessing


class ColorMapController(QtGui.QGroupBox):
    """Allows user to apply a colormap to an image."""

    colorMapChanged = QtCore.pyqtSignal()

    def __init__(self, parent) -> None:
        super(ColorMapController, self).__init__()

        self.parent = parent
        self.color_map = None
        self.color_map_max = None

        self.setTitle("Color Map")

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
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
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
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        self.gamma_lbl.hide()
        self.gamma_sbx = QtGui.QDoubleSpinBox()
        self.gamma_sbx.setMinimum(0.0001)
        self.gamma_sbx.setMaximum(1000)
        self.gamma_sbx.setSingleStep(0.1)
        self.gamma_sbx.hide()
        self.gamma_sbx.setValue(2.0)
        self.max_value_lbl = QtGui.QLabel("Max: ")
        self.max_value_lbl.setAlignment(
            QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter
        )
        self.max_value_sbx = QtGui.QSpinBox()
        self.max_value_sbx.setMinimum(1)
        self.max_value_sbx.setMaximum(1000000)
        self.max_value_sbx.setSingleStep(1)
        self.max_value_sbx.setValue(1000)

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.name_cbx, 0, 0, 1, 2)
        self.layout.addWidget(self.scale_cbx, 1, 0, 1, 2)
        self.layout.addWidget(self.base_lbl, 2, 0)
        self.layout.addWidget(self.base_sbx, 2, 1)
        self.layout.addWidget(self.gamma_lbl, 2, 0)
        self.layout.addWidget(self.gamma_sbx, 2, 1)
        self.layout.addWidget(self.max_value_lbl, 3, 0)
        self.layout.addWidget(self.max_value_sbx, 3, 1)

        # Connections
        self.name_cbx.currentIndexChanged.connect(self._setColorMap)
        self.scale_cbx.currentIndexChanged.connect(self._setColorMap)
        self.scale_cbx.currentIndexChanged.connect(self._toggleScaleOptions)
        self.n_pts_sbx.valueChanged.connect(self._setColorMap)
        self.base_sbx.valueChanged.connect(self._setColorMap)
        self.gamma_sbx.valueChanged.connect(self._setColorMap)
        self.max_value_sbx.valueChanged.connect(self._setColorMapBounds)

        # Sets initial color map
        self._setColorMap()
        self._setColorMapBounds()

    def _setColorMap(self) -> None:
        """Sets parameters for color map creation and emits signal."""

        self.name = self.name_cbx.currentText()
        self.scale = self.scale_cbx.currentText()
        self.n_pts = self.n_pts_sbx.value()
        self.base = self.base_sbx.value()
        self.gamma = self.gamma_sbx.value()

        self.color_map = createColorMap(
            name=self.name,
            scale=self.scale,
            base=self.base,
            gamma=self.gamma
        )

        self.colorMapChanged.emit()

    def _toggleScaleOptions(self) -> None:
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

    def _setColorMapBounds(self) -> None:
        """Sets maximum pixel value for color map."""

        self.color_map_max = self.max_value_sbx.value()
        self.colorMapChanged.emit()


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
        raise KeyError("Color map not found.")

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
