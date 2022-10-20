"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea

from imageanalysis.structures import Scan
from imageanalysis.ui.data_view.gridded_data import GriddedDataWidget
from imageanalysis.ui.data_view.raw_data import RawDataWidget


class PlotView(DockArea):
    """Houses a tab widget for DataViewTab objects."""

    def __init__(self) -> None:
        super(PlotView, self).__init__()

class PlotArea(pg.PlotWidget):
    ...

class PlotDetailsWidget(QtGui.QWidget):
    ...

    