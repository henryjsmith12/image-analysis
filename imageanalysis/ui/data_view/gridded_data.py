"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtGui

# ----------------------------------------------------------------------------------

from imageanalysis.ui.data_view.utils import ImageTool

# ==================================================================================

class GriddedDataWidget(QtGui.QWidget):

    def __init__(self) -> None:
        super(GriddedDataWidget, self).__init__()

        self.controller = GriddedDataController()
        self.image_tool_3d = ImageTool()
        self.image_tool_2d = ImageTool()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.controller, 0, 0, 1, 2)
        self.layout.addWidget(self.image_tool_3d, 1, 0, 3, 2)
        self.layout.addWidget(self.image_tool_2d, 4, 0, 3, 2)
        for i in range(self.layout.rowCount()):
            self.layout.setRowStretch(i, 1)
        for i in range(self.layout.columnCount()):
            self.layout.setRowStretch(i, 1)

# ==================================================================================

class GriddedDataController(QtGui.QWidget):

    def __init__(self) -> None:
        super(GriddedDataController, self).__init__()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)

# ==================================================================================