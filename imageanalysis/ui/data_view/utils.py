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

        self.image_view = ImageView()
        self.roi_widget = ROIWidget()

        self.dock_area = DockArea()
        self.image_view_dock = Dock(
            name="Image",
            size=(1, 1),
            widget=self.image_view,
            hideTitle=False,
            closable=False
        )
        self.roi_widget_dock = Dock(
            name="ROI", 
            size=(1, 1), 
            widget=self.roi_widget, 
            hideTitle=False, 
            closable=False
        )
        self.dock_area.addDock(self.roi_widget_dock)
        self.dock_area.addDock(self.image_view_dock, "above", self.roi_widget_dock)

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dock_area, 0, 0)

    # ------------------------------------------------------------------------------

    def setImage(self, data, image, x_label=None, y_label=None):
        self.image_view.setImage(image)

        # Color mapping test
        '''if self.data_max is None:
            self.data_max = np.amax(data)

        if self.cmap is None:
            n = 2048
            stops = np.logspace(0, len(str(int(self.data_max))), n) / (10 ** len(str(int(self.data_max))))
            colors = pg.getFromMatplotlib("jet").getLookupTable(nPts=n)

            self.cmap = pg.ColorMap(stops, colors)

            self.image_view.setColorMap(self.cmap)'''

        if x_label is not None:
            self.image_view.getView().setLabel("bottom", x_label)
        if y_label is not None:
            self.image_view.getView().setLabel("left", y_label)

# ==================================================================================

class ImageView(pg.ImageView):

    def __init__(self) -> None:
        super(ImageView, self).__init__(imageItem=pg.ImageItem(), view=pg.PlotItem())
        #self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()
    
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