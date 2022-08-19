"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui
from pyqtgraph.dockarea import Dock, DockArea
from sklearn import preprocessing


class ImageTool(QtGui.QWidget):
    """Allows user to view and manipulate images."""

    def __init__(self) -> None:
        super(ImageTool, self).__init__()

        self.data_max = None
        self.cmap = None
        self.cbar = None

        # Child widgets
        self.image_view = ImageView()

        # Docks
        self.dock_area = DockArea()
        self.image_view_dock = Dock(
            name="Image",
            size=(1, 1),
            widget=self.image_view,
            hideTitle=True,
            closable=False
        )
        self.dock_area.addDock(self.image_view_dock)

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dock_area, 0, 0)

    def setImage(
        self,
        data: np.ndarray,
        image: np.ndarray,
        x_label: str=None,
        y_label: str=None,
        x_coords: np.ndarray=None,
        y_coords: np.ndarray=None,
        slice_label: str=None,
        slice_coord: float=None
    ):
        # For first-time runthrough
        if self.data_max is None:
            self.data_max = float(np.amax(data))
        if self.cmap is None:
            self.setColorMap()
        if self.cbar is None:
            self.cbar = pg.ColorBarItem(
                values=(0, self.data_max),
                cmap=self.cmap,
                interactive=False,
                width=15,
                label="Intensity",
                orientation="h"
            )
            self.cbar.setImageItem(
                img=image,
                insert_in=self.image_view.getView()
            )

        # Sets axis labels if given
        if x_label is not None:
            self.image_view.getView().setLabel("bottom", x_label)
        if y_label is not None:
            self.image_view.getView().setLabel("left", y_label)

        # Sets image transform if given
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

    def setCoordinates(self):
        ...

    def setLabels(self):
        ...

    def setColorMap(self):
        """Sets colormap for image."""

        self.cmap = createColorMap(
            name="jet",
            scale="power",
            min=0,
            max=self.data_max
        )

        self.image_view.setColorMap(self.cmap)

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

class ColorMapWidget(QtGui.QWidget):
    """Allows user to apply a colormap to an image."""

    def __init__(self) -> None:
        super(ColorMapWidget, self).__init__()

        ...


def createColorMap(
    name: str, 
    scale: str, 
    min: float, 
    max: float,
    n_pts: int=128,
    base: float=1.75,
    gamma: float=2
) -> pg.ColorMap:
    
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
    
