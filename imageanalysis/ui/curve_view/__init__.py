"""Copyright (c) UChicago Argonne, LLC. All rights reserved.

See LICENSE file.
"""


import numpy as np
from PyQt5 import QtWidgets
import pyqtgraph as pg
from pyqtgraph import QtCore
from pyqtgraph.dockarea import Dock, DockArea
from random import randint

from imageanalysis.structures import Curve
from imageanalysis.ui.data_view.gridded_data import GriddedDataWidget
from imageanalysis.ui.data_view.raw_data import RawDataWidget


class CurveView(QtWidgets.QWidget):
    """Houses a tab widget for DataViewTab objects."""

    def __init__(self, parent=None) -> None:
        super(CurveView, self).__init__()
        self.parent = parent

        self.setEnabled(False)

        self.curves = []

        # Widgets
        self.curve_plot = CurvePlot(parent=self)
        self.curve_ctrl = CurveController(parent=self)

        # Docks
        self.dock_area = DockArea()
        self.curve_plot_dock = Dock(
            name="Curve Plot",
            size=(1, 1),
            widget=self.curve_plot,
            hideTitle=True,
            closable=False
        )
        self.curve_ctrl_dock = Dock(
            name="Curve Controller",
            size=(1, 2),
            widget=self.curve_ctrl,
            hideTitle=True,
            closable=False
        )
        self.dock_area.addDock(self.curve_plot_dock)
        self.dock_area.addDock(
            self.curve_ctrl_dock,
            "bottom",
            self.curve_plot_dock
        )
        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.dock_area)


    def _addCurve(self, curve: Curve) -> None:
        self.curves.append(curve)
        self.curve_ctrl._addCurve(curve)
        

# TODO: Rename to curve controller
class CurveController(QtWidgets.QWidget):

    plot_axis_updated = QtCore.pyqtSignal()

    def __init__(self, parent=None) -> None:
        super().__init__()
        self.parent = parent
        self.curve_plot = parent.curve_plot

        self.x_axis_lbl = QtWidgets.QLabel("x-axis: ")
        self.x_axis_cbx = QtWidgets.QComboBox()
        self.x_axis_options = ["Index", "x", "y", "t", "H", "K", "L"]
        self.x_axis_cbx.addItems(self.x_axis_options)
        self.curve_list_items = []
        self.curve_table = QtWidgets.QTableWidget(0, 3)
        self.curve_table.setHorizontalHeaderLabels(["Show", "Color", ""])

        self.curve_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.curve_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.curve_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)

        self.layout = QtWidgets.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.x_axis_lbl, 0, 0)
        self.layout.addWidget(self.x_axis_cbx, 0, 1)
        self.layout.addWidget(self.curve_table, 1, 0, 7, 2)

        self.x_axis_cbx.currentTextChanged.connect(self._updatePlotAxis)

    def _addCurve(self, curve: Curve) -> None:
        cli = CurveListItem(curve=curve, parent=self)
        self.curve_list_items.append(cli)
        self.curve_table.insertRow(self.curve_table.rowCount())

        self.curve_table.setCellWidget(self.curve_list_items.index(cli), 0, cli.vis_chkbx)
        self.curve_table.setCellWidget(self.curve_list_items.index(cli), 1, cli.color_btn)
        self.curve_table.setCellWidget(self.curve_list_items.index(cli), 2, cli.delete_btn)
    
    def _updatePlotAxis(self):
        for cli in self.curve_list_items:
            cli._toggleCoordinates()


class CurveListItem:
    def __init__(self, curve: Curve, parent) -> None:
        self.curve = curve
        self.parent = parent
        self.curve_plot = parent.curve_plot

        self.vis_chkbx = QtWidgets.QCheckBox()
        self.vis_chkbx.setChecked(True)
        self.color_btn = pg.ColorButton(
            color=(
                randint(0, 255),
                randint(0, 255),
                randint(0, 255)
            )
        )
        self.delete_btn = QtWidgets.QPushButton("Delete")
        self.type = ""
        self.scan = ""
        self.coords = {
            "Index": range(0, len(curve.data)),
            curve.labels[0]: curve.coords[0],
            curve.labels[1]: curve.coords[1],
            curve.labels[2]: curve.coords[2]
        }

        self.plot_data_item = pg.PlotDataItem()
        self.plot_data_item.setPen(pg.mkPen(self.color_btn.color(), width=2))
        self._toggleCoordinates()
        

        self.curve_plot.addItem(self.plot_data_item)

        self.vis_chkbx.stateChanged.connect(self._toggleVisibility)
        self.color_btn.sigColorChanged.connect(self._toggleColor)
        self.delete_btn.clicked.connect(self._delete)

    def _toggleColor(self):
        color = self.color_btn.color()
        pen = pg.mkPen(color, width=2)
        self.plot_data_item.setPen(pen)

    def _toggleVisibility(self):
        if self.vis_chkbx.isChecked():
            self.plot_data_item.show()
        else:
            self.plot_data_item.hide()

    def _toggleCoordinates(self):
        x_coords = self.parent.x_axis_cbx.currentText()
        if x_coords in self.coords.keys():
            self.plot_data_item.show()
            self.plot_data_item.setData(
                x=self.coords[x_coords],
                y=self.curve.data
            )
        else:
            self.plot_data_item.hide()

    def _delete(self):
        self.curve_plot.removeItem(self.plot_data_item)
        item_index = self.parent.curve_list_items.index(self)
        self.parent.curve_table.removeRow(item_index)
        self.parent.curve_list_items.pop(item_index)
        del(self)


class CurvePlot(pg.PlotWidget):
    def __init__(self, parent=None, background='w'):
        super().__init__(parent, background)


class CurvePlotController(QtWidgets.QWidget):
    ...
