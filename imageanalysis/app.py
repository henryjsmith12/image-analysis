"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from PyQt5 import QtWidgets
import sys

from imageanalysis.ui.main_window import MainWindow


def run() -> None:
    """Package driver function."""

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == "__main__":
    sys.exit(run())
    
