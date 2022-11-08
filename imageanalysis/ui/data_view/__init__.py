"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from PyQt5 import QtWidgets
from pyqtgraph import QtCore

from imageanalysis.structures import Scan
from imageanalysis.ui.data_view.gridded_data import GriddedDataWidget
from imageanalysis.ui.data_view.raw_data import RawDataWidget


class DataView(QtWidgets.QTabWidget):
    """Houses a tab widget for DataViewTab objects."""

    def __init__(self, parent=None) -> None:
        super(DataView, self).__init__()
        self.parent = parent

        self.scan_list = []
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self._closeTab)

    def _addScan(self, scan: Scan) -> None:
        """Adds new DataViewTab."""

        tab_title = str(scan.number)
        self.addTab(DataViewTab(scan=scan, parent=self), tab_title)

    def _closeTab(self, index: int) -> None:
        """Closes DataViewTab at specific index."""

        w = self.widget(index)
        w.deleteLater()
        self.removeTab(index)


class DataViewTab(QtWidgets.QWidget):
    """Houses various widgets to view data with."""

    def __init__(self, scan: Scan, parent=None) -> None:
        super(DataViewTab, self).__init__()
        self.parent=parent

        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.scan = scan

        # Child widgets
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(
            RawDataWidget(scan=scan, parent=self),
            "Raw"
        )
        self.tab_widget.addTab(
            GriddedDataWidget(scan=scan, parent=self), 
            "Gridded"
        )

        # Layout
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)
