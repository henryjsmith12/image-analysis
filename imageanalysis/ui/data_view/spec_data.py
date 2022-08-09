"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


from pyqtgraph import QtGui


class SpecDataWidget(QtGui.QWidget):
    """Allows user to explore SPEC data for a scan."""

    def __init__(self) -> None:
        super(SpecDataWidget, self).__init__()

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
