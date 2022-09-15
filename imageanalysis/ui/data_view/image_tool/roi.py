import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtGui


class ROIController(QtGui.QGroupBox):

    def __init__(
        self, 
        parent_plot,
        child_plot,
        image_tool,
        title=None
    ) -> None:
        super().__init__()

        self.parent_plot = parent_plot
        self.child_plot = child_plot
        self.image_tool = image_tool
        self.setTitle(title)

        self.roi = None

        self.roi_type_lbl = QtGui.QLabel("ROI Type: ")
        self.roi_type_cbx = QtGui.QComboBox()
        self.roi_types = ["none", "line"]
        self.roi_type_cbx.addItems(self.roi_types)
        self.roi_details_gbx = QtGui.QGroupBox()
        self.roi_details_gbx_layout = QtGui.QGridLayout()
        self.roi_details_gbx.setLayout(self.roi_details_gbx_layout)
        self.center_btn = QtGui.QPushButton("Center")
        self.calc_type_cbx = QtGui.QComboBox()
        self.roi_details_gbx_layout.addWidget(self.center_btn, 0, 0)
        self.roi_details_gbx_layout.addWidget(self.calc_type_cbx, 1, 0)
        self.roi_details_gbx.hide()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.roi_type_lbl, 0, 0)
        self.layout.addWidget(self.roi_type_cbx, 0, 1)
        self.layout.addWidget(self.roi_details_gbx, 1, 0, 1, 2)

        self.roi_type_cbx.currentTextChanged.connect(self._changeROIType)

    def _changeROIType(self):
        if self.roi_type_cbx.currentText() == "none":
            if self.roi is not None:
                self.parent_plot.removeItem(self.roi)
                self.roi = None
            self.child_plot._hide()
            self.roi_details_gbx.hide()
        elif self.roi_type_cbx.currentText() == "line":
            self.parent_plot.removeItem(self.roi)
            self.roi = LineSegmentROI(parent=self.parent_plot, child=self.child_plot)
            self.parent_plot.addItem(self.roi)
            self.center_btn.clicked.connect(self.roi._center)
            self.calc_type_cbx.clear()
            self.calc_types = ["values"]
            self.calc_type_cbx.addItems(self.calc_types)
            self.child_plot._show()
            self.roi_details_gbx.show()
            self.roi._getSlice()
            self.parent_plot.image_tool.controller._setColorMap()

class LineSegmentROI(pg.LineSegmentROI):

    def __init__(
        self, 
        parent, 
        child
    ) -> None:

        self.parent_plot = parent
        self.child_plot = child
        self.image_tool = self.parent_plot.image_tool

        x_1, y_1 = self.parent_plot.x_coords[0], self.parent_plot.y_coords[0]
        x_2, y_2 = self.parent_plot.x_coords[-1], self.parent_plot.y_coords[-1]

        super(LineSegmentROI, self).__init__(
            positions=((x_1, y_1), (x_2, y_2))
        )

        self.sigRegionChanged.connect(self._getSlice)
        self.image_tool.colorMapUpdated.connect(self._getSlice)

    def _center(self):
        x_1, y_1 = self.parent_plot.x_coords[0], self.parent_plot.y_coords[0]
        x_2, y_2 = self.parent_plot.x_coords[-1], self.parent_plot.y_coords[-1]
        self.movePoint(self.getHandles()[0], (x_1, y_1))
        self.movePoint(self.getHandles()[1], (x_2, y_2))

    def _getSlice(self):

        data, coords = self.getArrayRegion(
            data=self.parent_plot.image_tool.data, 
            img=self.parent_plot.getImageItem(), 
            returnMappedCoords=True
        )
        self.x_coords, self.y_coords = coords.astype(int)

        from imageanalysis.ui.data_view.gridded_data import \
            GriddedDataWidget
        from imageanalysis.ui.data_view.raw_data import \
            RawDataWidget

        if type(self.image_tool.parent) == RawDataWidget:
            data = self.image_tool.parent.scan.raw_image_data
            slice = []

            for i in range(data.shape[0]):
                for x, y in zip(self.x_coords, self.y_coords):
                    if 0 <= x < data.shape[1] and 0 <= y < data.shape[2]:
                        slice.append(data[i, x, y])
                    else:
                        slice.append(0)
            slice = np.array(slice).reshape((data.shape[0], len(self.x_coords)))
            self.child_plot._plot(
                image=slice, 
                x_label="t",
                y_axis=False
            )

        # GriddedDataWidget
        elif type(self.image_tool.parent) == GriddedDataWidget:
            dim_order = self.image_tool.parent.controller.dim_order
            data = np.transpose(self.image_tool.data, dim_order)
            x_label = ["H", "K", "L"][dim_order[2]]
            x_coords = self.image_tool.parent.controller.coords[dim_order[2]]

            slice = []
            for i in range(data.shape[2]):
                for x, y in zip(self.x_coords, self.y_coords):
                    if 0 <= x < data.shape[0] and 0 <= y < data.shape[1]:
                        slice.append(data[x, y, i])
                    else:
                        slice.append(0)
            slice = np.array(slice).reshape((data.shape[2], len(self.x_coords)))
            self.child_plot._plot(
                image=slice,
                x_label=x_label,
                x_coords=x_coords,
                y_axis=False
            )


class RectROI(pg.RectROI):

    def __init__(self, pos, size, centered=False, sideScalers=False, **args):
        super().__init__(pos, size, centered, sideScalers, **args)

class CircleROI(pg.CircleROI):

    def __init__(self, pos, size=None, radius=None, **args):
        super().__init__(pos, size, radius, **args)

class PolygonROI(pg.PolygonROI):

    def __init__(self, positions, pos=None, **args):
        super().__init__(positions, pos, **args)