"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import sys

from pyqtgraph import QtGui

from imageanalysis.ui.main_window import MainWindow


def run() -> None:
    """Package driver function."""

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    run()
