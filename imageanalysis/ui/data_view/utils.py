"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import pyqtgraph as pg
from pyqtgraph import QtGui
from pyqtgraph.dockarea import Dock, DockArea

# ==================================================================================

class ImageTool(QtGui.QWidget):

    def __init__(self) -> None:
        super(ImageTool, self).__init__()

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

    def setImage(self, image):
        self.image_view.setImage(image)

# ==================================================================================

class ImageView(pg.ImageView):

    def __init__(self) -> None:
        super(ImageView, self).__init__(imageItem=pg.ImageItem(), view=pg.PlotItem())
        self.ui.histogram.hide()
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