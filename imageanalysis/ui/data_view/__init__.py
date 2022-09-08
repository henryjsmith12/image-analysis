"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from pyqtgraph import QtCore, QtGui

from imageanalysis.structures import Scan
from imageanalysis.ui.data_view.gridded_data import GriddedDataWidget
from imageanalysis.ui.data_view.raw_data import RawDataWidget


class DataView(QtGui.QTabWidget):
    """Houses a tab widget for DataViewTab objects."""

    def __init__(self) -> None:
        super(DataView, self).__init__()

        self.scan_list = []
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self._closeTab)

    def _addScan(self, scan: Scan) -> None:
        """Adds new DataViewTab."""

        tab_title = str(scan.number)
        self.addTab(DataViewTab(scan=scan), tab_title)

    def _closeTab(self, index: int) -> None:
        """Closes DataViewTab at specific index."""

        w = self.widget(index)
        w.deleteLater()
        self.removeTab(index)


class DataViewTab(QtGui.QWidget):
    """Houses various widgets to view data with."""

    def __init__(self, scan: Scan) -> None:
        super(DataViewTab, self).__init__()

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.scan = scan

        # Child widgets
        self.tab_widget = QtGui.QTabWidget()
        self.tab_widget.addTab(RawDataWidget(scan=scan), "Raw")
        self.tab_widget.addTab(GriddedDataWidget(scan=scan), "Gridded")

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)
