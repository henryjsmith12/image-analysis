"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea
from random import randint

from imageanalysis.structures import Curve
from imageanalysis.ui.data_view.gridded_data import GriddedDataWidget
from imageanalysis.ui.data_view.raw_data import RawDataWidget


class PlotView(QtGui.QWidget):
    """Houses a tab widget for DataViewTab objects."""

    def __init__(self, parent=None) -> None:
        super(PlotView, self).__init__()
        self.parent = parent

        self.curves = []

        # Widgets
        self.curve_plot = CurvePlot(parent=self)
        self.curve_list_widget = CurveListWidget(parent=self)

        # Docks
        self.dock_area = DockArea()
        self.curve_plot_dock = Dock(
            name="Curve Plot",
            size=(1, 1),
            widget=self.curve_plot,
            hideTitle=True,
            closable=False
        )
        self.curve_list_dock = Dock(
            name="Select Scan",
            size=(1, 2),
            widget=self.curve_list_widget,
            hideTitle=True,
            closable=False
        )
        self.dock_area.addDock(self.curve_plot_dock)
        self.dock_area.addDock(
            self.curve_list_dock,
            "bottom",
            self.curve_plot_dock
        )
        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dock_area)


    def _addCurve(self, curve: Curve) -> None:
        self.curves.append(curve)
        self.curve_list_widget._addCurve(curve)
        

class CurveListWidget(QtGui.QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__()
        self.parent = parent
        self.curve_plot = parent.curve_plot

        self.curve_list_items = []

        self.curve_table = QtGui.QTableWidget(1, 5)
        self.curve_table.setHorizontalHeaderLabels(["Show", "Color", "Type", "Scan", "x-axis"])

        self.curve_table.horizontalHeader().setSectionResizeMode(0, QtGui.QHeaderView.ResizeToContents)
        self.curve_table.horizontalHeader().setSectionResizeMode(1, QtGui.QHeaderView.ResizeToContents)
        self.curve_table.horizontalHeader().setSectionResizeMode(2, QtGui.QHeaderView.ResizeToContents)
        self.curve_table.horizontalHeader().setSectionResizeMode(3, QtGui.QHeaderView.ResizeToContents)
        self.curve_table.horizontalHeader().setSectionResizeMode(4, QtGui.QHeaderView.Stretch)


        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.curve_table)

    def _addCurve(self, curve: Curve) -> None:
        cli = CurveListItem(curve=curve, parent=self)
        self.curve_list_items.append(cli)

        self.curve_table.setCellWidget(self.curve_list_items.index(cli), 0, cli.vis_chkbx)
        self.curve_table.setCellWidget(self.curve_list_items.index(cli), 1, cli.color_btn)
        self.curve_table.setCellWidget(self.curve_list_items.index(cli), 2, QtGui.QLabel(cli.type))
        self.curve_table.setCellWidget(self.curve_list_items.index(cli), 3, QtGui.QLabel(cli.scan))
        self.curve_table.setCellWidget(self.curve_list_items.index(cli), 4, cli.coord_type_cbx)
    

class CurveListItem:
    def __init__(self, curve: Curve, parent) -> None:
        self.curve = curve
        self.parent = parent
        self.curve_plot = parent.curve_plot

        self.vis_chkbx = QtGui.QCheckBox()
        self.vis_chkbx.setChecked(True)
        self.color_btn = pg.ColorButton(
            color=(
                randint(0, 200),
                randint(0, 200),
                randint(0, 200)
            )
        )
        self.type = ""
        self.scan = ""
        self.coords = {
            "Index": range(0, len(curve.data)),
            curve.labels[0]: curve.coords[0],
            curve.labels[1]: curve.coords[1],
            curve.labels[2]: curve.coords[2]
        }

        self.coord_type_cbx = QtGui.QComboBox()
        self.coord_type_cbx.addItems(self.coords.keys())

        self.plot_data_item = ...

        self.curve_plot.plot(
            x=self.coords[self.coord_type_cbx.currentText()],
            y=curve.data, 
            pen=pg.mkPen(self.color_btn.color(), width=1.5)
        )

    def _toggleColor(self):
        ...

    def _toggleVisibility(self):
        ...

    def _toggleCoordinateType(self):
        ...

class CurvePlot(pg.PlotWidget):
    def __init__(self, parent=None, background='w'):
        super().__init__(parent, background)


class CurvePlotController(QtGui.QWidget):
    ...


