"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui

# ==================================================================================

class DataViewWidget(QtGui.QWidget):
    
    def __init__(self) -> None:
        super(DataViewWidget, self).__init__()

        self.tab_widget = QtGui.QTabWidget()
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)

# ==================================================================================