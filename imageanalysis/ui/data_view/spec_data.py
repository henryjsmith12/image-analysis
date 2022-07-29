"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui

# ==================================================================================

class SpecDataWidget(QtGui.QWidget):

    def __init__(self) -> None:
        super(SpecDataWidget, self).__init__()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

# ==================================================================================