"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

import imp
from pyqtgraph import QtGui

# ----------------------------------------------------------------------------------

from imageanalysis.structures import Scan
from imageanalysis.ui.data_view.gridded_data import GriddedDataWidget
from imageanalysis.ui.data_view.raw_data import RawDataWidget
from imageanalysis.ui.data_view.spec_data import SpecDataWidget

# ==================================================================================

class DataView(QtGui.QTabWidget):
    
    def __init__(self) -> None:
        super(DataView, self).__init__()

        self.scan_list = []

    # ------------------------------------------------------------------------------

    def addScan(self, scan: Scan):
        self.addTab(DataViewTab(scan), str(scan.number))

# ==================================================================================

class DataViewTab(QtGui.QWidget):

    def __init__(self, scan: Scan) -> None:
        super(DataViewTab, self).__init__()

        self.scan = scan

        self.tab_widget = QtGui.QTabWidget()
        #self.tab_widget.addTab(SpecDataWidget(), "SPEC")
        self.tab_widget.addTab(RawDataWidget(scan), "Raw")
        self.tab_widget.addTab(GriddedDataWidget(scan), "Gridded")
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)

# ==================================================================================