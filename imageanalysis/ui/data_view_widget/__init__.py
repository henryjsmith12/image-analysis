"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui

# ==================================================================================

class DataViewWidget(QtGui.QTabWidget):
    
    def __init__(self) -> None:
        super(DataViewWidget, self).__init__()

# ==================================================================================

class DataViewTab(QtGui.QWidget):

    def __init__(self) -> None:
        super(DataViewTab, self).__init__()

        self.tab_widget = QtGui.QTabWidget()
        self.tab_widget.addTab(QtGui.QWidget(), "SPEC")
        self.tab_widget.addTab(QtGui.QWidget(), "Raw")
        self.tab_widget.addTab(QtGui.QWidget(), "Gridded")
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)

# ==================================================================================