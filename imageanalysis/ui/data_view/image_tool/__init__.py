import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui
from pyqtgraph.dockarea import Dock, DockArea

class ImageTool(DockArea):

    def __init__(self) -> None:
        super().__init__()

        self.plot_3d = ImagePlot(parent=self)
        self.plot_2d = ImagePlot(parent=self)
        self.plot_1d = LinePlot(parent=self)
        self.controller = ImageToolController(parent=self)
        
        self.plot_3d_dock = Dock(
            name="3D Image Plot",
            size=(10, 10),
            widget=self.plot_3d,
            hideTitle=True,
            closable=False
        )
        self.plot_2d_dock = Dock(
            name="2D Image Plot",
            size=(10, 10),
            widget=self.plot_2d,
            hideTitle=True,
            closable=False
        )
        self.plot_1d_dock = Dock(
            name="Line Plot",
            size=(10, 10),
            widget=self.plot_1d,
            hideTitle=True,
            closable=False
        )
        self.controller_dock = Dock(
            name="Color Mapping",
            size=(10, 1),
            widget=self.controller,
            hideTitle=True,
            closable=False
        )
        self.addDock(self.controller_dock)
        self.addDock(self.plot_3d_dock, "left", self.controller_dock)
        self.addDock(self.plot_2d_dock, "bottom", self.plot_3d_dock)
        self.addDock(self.plot_1d_dock, "bottom", self.plot_2d_dock)

        # If ROI is activated, proper dock will show
        '''self.plot_2d_dock.hide()
        self.plot_1d_dock.hide()'''


    def _setImage(
        self,
        image: np.ndarray,
        data: np.ndarray,
        x_label: str=None,
        y_label: str=None,
        x_coords: list=None,
        y_coords: list=None
    ):
        self.data = data
        self.plot_3d._setLabels(x=x_label, y=y_label)
        self.plot_3d._setImage(image=image)
        self.plot_3d._setCoordinates(x=x_coords, y=y_coords)


class ImageToolController(QtGui.QWidget):

    def __init__(self, parent) -> None:
        super().__init__()

        self.image_tool = parent

        # Color Map
        # Mouse
        # Options for 2 Image Plots
        # Options for Line Plot

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

class ImagePlot(pg.ImageView):

    def __init__(self, parent) -> None:
        super(ImagePlot, self).__init__(
            imageItem=pg.ImageItem(),
            view=pg.PlotItem()
        )

        self.image_tool = parent
        self.image = None
        self.transform = None

        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()
        self.getView().setAspectLocked(False)
        self.getView().ctrlMenu = None

    def _setImage(self, image: np.ndarray):
        self.image = image
        self.setImage(
            img=image,
            autoRange=False,
            autoLevels=False,
            transform=self.transform
        )
    
    def _setLabels(self, x: str=None, y: str=None) -> None:
        if x is not None and type(x) == str:
            self.getView().setLabel("bottom", x)
        if y is not None and type(y) == str:
            self.getView().setLabel("left", y)

    def _setCoordinates(self, x=None, y=None):
        if self.image is not None:
            self.transform = QtGui.QTransform()

            if x is None:
                x = np.linspace(
                    start=0, 
                    stop=self.image.shape[0] - 1, 
                    num=self.image.shape[0],
                    endpoint=False
                )

            if y is None:
                y = np.linspace(
                    start=0, 
                    stop=self.image.shape[1] - 1, 
                    num=self.image.shape[1],
                    endpoint=False
                )

            scale = (x[1] - x[0], y[1] - y[0])
            pos = (x[0], y[0])
            self.transform.translate(*pos)
            self.transform.scale(*scale)
        else:
            self.transform = None


class LinePlot(pg.PlotWidget):

    def __init__(self, parent) -> None:
        super().__init__()

        self.image_tool = parent

    def _setData():
        ...

    def _setLabels():
        ...