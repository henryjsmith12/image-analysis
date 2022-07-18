"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui

# ==================================================================================

class MainWindow(QtGui.QWidget):
    
    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        # Window attributes
        self.setMinimumSize(1400, 800)
        self.setGeometry(0, 50, 1400, 800)
        self.setWindowTitle("image-analysis")

        self.layout = QtGui.QGridLayout()

        print(self.minimumSize())


