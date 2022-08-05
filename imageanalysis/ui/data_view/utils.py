"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui
from pyqtgraph.dockarea import Dock, DockArea

# ==================================================================================

class ImageTool(QtGui.QWidget):

    def __init__(self) -> None:
        super(ImageTool, self).__init__()

        self.data_max = None
        self.cmap = None
        self.cbar = None

        self.image_view = ImageView()
        self.roi_widget = ROIWidget()

        self.dock_area = DockArea()
        self.image_view_dock = Dock(
            name="Image",
            size=(1, 1),
            widget=self.image_view,
            hideTitle=True,
            closable=False
        )
        self.roi_widget_dock = Dock(
            name="ROI", 
            size=(1, 1), 
            widget=self.roi_widget, 
            hideTitle=False, 
            closable=False
        )
        self.dock_area.addDock(self.image_view_dock)

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dock_area, 0, 0)

    # ------------------------------------------------------------------------------

    def setImage(self, data, image, x_label=None, y_label=None, x_coords=None, y_coords=None, slice_label=None, slice_value=None):

        # Color mapping test
        if self.data_max is None:

            self.data_max = float(np.amax(data))

        #image = image.astype("float64")

        if self.cmap is None:
            n_pts = 1024
            base = 2
            
            stops = np.logspace(start=0, stop=len(str(int(self.data_max))), num=n_pts, base=base) / (base ** len(str(int(self.data_max))))
            #stops = np.linspace(start=0, stop=1.0, num=n_pts)

            colors = pg.getFromMatplotlib("jet").getLookupTable(nPts=n_pts)

            self.cmap = pg.ColorMap(stops, colors)
            
            self.image_view.setColorMap(self.cmap)

        if self.cbar is None:
            self.cbar = pg.ColorBarItem(values=(0, self.data_max), cmap=self.cmap, interactive=False, width=15, label="Intensity", orientation="h")
            self.cbar.setImageItem(img=image, insert_in=self.image_view.getView())

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

        if slice_label is not None and slice_value is not None:  
            self.image_view.getView().setTitle(f"{slice_label}={slice_value}")

        self.image_view.setImage(image, autoRange=False, autoLevels=False, transform=tr)

# ==================================================================================

class ImageView(pg.ImageView):

    def __init__(self) -> None:
        super(ImageView, self).__init__(imageItem=pg.ImageItem(), view=pg.PlotItem())
        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()

        self.getView().setAspectLocked(False)

    # ------------------------------------------------------------------------------

    def setScale(self):
        ...

    # ------------------------------------------------------------------------------

    def setColormap(self):
        ...

# ==================================================================================

class ROIWidget(QtGui.QWidget):

    def __init__(self) -> None:
        super(ROIWidget, self).__init__()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

# ==================================================================================