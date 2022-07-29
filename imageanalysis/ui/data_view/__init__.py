"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui

# ----------------------------------------------------------------------------------

from imageanalysis.ui.data_view.gridded_data import GriddedDataWidget
from imageanalysis.ui.data_view.raw_data import RawDataWidget
from imageanalysis.ui.data_view.spec_data import SpecDataWidget

# ==================================================================================

class DataView(QtGui.QTabWidget):
    
    def __init__(self) -> None:
        super(DataView, self).__init__()

        self.addTab(DataViewTab(), "840")

# ==================================================================================

class DataViewTab(QtGui.QWidget):

    def __init__(self) -> None:
        super(DataViewTab, self).__init__()

        self.tab_widget = QtGui.QTabWidget()
        #self.tab_widget.addTab(SpecDataWidget(), "SPEC")
        self.tab_widget.addTab(RawDataWidget(), "Raw")
        self.tab_widget.addTab(GriddedDataWidget(), "Gridded")
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)

# ==================================================================================