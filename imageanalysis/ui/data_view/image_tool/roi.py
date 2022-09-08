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