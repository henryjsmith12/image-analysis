"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui
import sys

# ----------------------------------------------------------------------------------

from imageanalysis.ui.main_window import MainWindow

# ==================================================================================

def run():
    """
    Package driver function.
    """

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

# ==================================================================================

if __name__ == "__main__":
    run()