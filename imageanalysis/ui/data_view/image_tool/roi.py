import pyqtgraph as pg
from pyqtgraph import QtGui

from imageanalysis.ui.data_view.image_tool import ImagePlot

class ROIController(QtGui.QWidget):

    def __init__(self) -> None:
        super().__init__()

class LineSegmentROI(pg.LineSegmentROI):

    def __init__(
        self,
        parent_plot: ImagePlot,
        child_plot
    ) -> None:
        super().__init__()

    def _getSlice(self) -> None:
        ...

    def _setImage(self) -> None:
        ...

class RectROI(pg.RectROI):

    def __init__(self, pos, size, centered=False, sideScalers=False, **args):
        super().__init__(pos, size, centered, sideScalers, **args)

class CircleROI(pg.CircleROI):

    def __init__(self, pos, size=None, radius=None, **args):
        super().__init__(pos, size, radius, **args)

class PolygonROI(pg.PolygonROI):

    def __init__(self, positions, pos=None, **args):
        super().__init__(positions, pos, **args)