"""
Copyright (c) UChicago Argonne, LLC. All rights reserved.
See LICENSE file.
"""

# ==================================================================================

from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea

# ----------------------------------------------------------------------------------

from imageanalysis.ui.data_view.utils import ImageTool

# ==================================================================================

class RawDataWidget(DockArea):

    def __init__(self, scan) -> None:
        super(RawDataWidget, self).__init__()

        self.scan = scan

        self.image_tool_3d = ImageTool()
        self.image_tool_2d = ImageTool()
        self.controller = RawDataController(scan, self.image_tool_3d)

        self.controller_dock = Dock(
            name="Controller",
            size=(1, 1),
            widget=self.controller,
            hideTitle=True,
            closable=False
        )
        self.image_tool_3d_dock = Dock(
            name="Controller",
            size=(1, 5),
            widget=self.image_tool_3d,
            hideTitle=True,
            closable=False
        )
        self.image_tool_2d_dock = Dock(
            name="Controller",
            size=(1, 5),
            widget=self.image_tool_2d,
            hideTitle=True,
            closable=False
        )
        self.controller_dock.setMaximumHeight(75)
        self.addDock(self.controller_dock)
        self.addDock(self.image_tool_3d_dock, "bottom" ,self.controller_dock)
        #self.addDock(self.image_tool_2d_dock, "bottom" ,self.image_tool_3d_dock)

# ==================================================================================

class RawDataController(QtGui.QWidget):

    def __init__(self, scan, image_tool) -> None:
        super(RawDataController, self).__init__()

        self.data = scan.raw_image_data
        self.scan = scan
        self.image_tool = image_tool

        # Child widgets
        self.data_slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.data_slider.setMaximum(self.data.shape[0] - 1)
        self.data_sbx = QtGui.QSpinBox()
        self.data_sbx.setMaximum(self.data.shape[0] - 1)
        self.data_type_rbg = QtGui.QButtonGroup()
        self.h_rbtn = QtGui.QRadioButton("H")
        self.k_rbtn = QtGui.QRadioButton("K")
        self.l_rbtn = QtGui.QRadioButton("L")
        self.intensity_rbtn = QtGui.QRadioButton("Intensity")
        self.intensity_rbtn.setChecked(True)
        for btn in [self.h_rbtn, self.k_rbtn, self.l_rbtn, self.intensity_rbtn]:
            self.data_type_rbg.addButton(btn)

        # Layout
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.data_slider, 0, 0, 1, 3)
        self.layout.addWidget(self.data_sbx, 0, 3, 1, 1)
        #self.layout.addWidget(self.h_rbtn, 1, 0, 1, 1)
        #self.layout.addWidget(self.k_rbtn, 1, 1, 1, 1)
        #self.layout.addWidget(self.l_rbtn, 1, 2, 1, 1)
        #self.layout.addWidget(self.intensity_rbtn, 1, 3, 1, 1)
        '''for i in range(self.layout.rowCount()):
            self.layout.setRowStretch(i, 1)'''
        for i in range(self.layout.columnCount()):
            self.layout.setColumnStretch(i, 1)

        # Connections
        for btn in [self.h_rbtn, self.k_rbtn, self.l_rbtn, self.intensity_rbtn]:
            btn.toggled.connect(self.setDataType)
            btn.toggled.connect(self.setImage)
        self.data_slider.valueChanged.connect(self.setIndex)
        self.data_slider.valueChanged.connect(self.setImage)
        self.data_sbx.valueChanged.connect(self.setIndex)
        self.data_sbx.valueChanged.connect(self.setImage)

        # Display first image
        self.setImage()

    # ------------------------------------------------------------------------------

    def setDataType(self):
        btn = self.sender()
        if btn.isChecked():
            if btn.text() == "Intensity":
                self.data = self.scan.raw_image_data
            elif btn.text() == "H":
                self.data = self.scan.h_map
            elif btn.text() == "K":
                self.data = self.scan.k_map
            elif btn.text() == "L":
                self.data = self.scan.l_map

            self.data_slider.setMaximum(self.data.shape[0] - 1)
            self.data_sbx.setMaximum(self.data.shape[0] - 1)

    # ------------------------------------------------------------------------------

    def setIndex(self):
        sender = self.sender()
        index = sender.value()
        if sender == self.data_slider:
            self.data_sbx.setValue(index)
        elif sender == self.data_sbx:
            self.data_slider.setValue(index)

    # ------------------------------------------------------------------------------

    def setImage(self):
        index = self.data_sbx.value()
        image = self.data[index]

        self.image_tool.setImage(self.data, image)

# ==================================================================================