import numpy as np
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
from pyqtgraph.dockarea import Dock, DockArea

from imageanalysis.ui.data_view.image_tool.color_mapping import ColorMapController

class ImageTool(DockArea):

    def __init__(self, parent) -> None:
        super().__init__()

        self.parent = parent

        self.data = None
        self.data_min, self.data_max = None, None
        self.color_map_max = 1
        self.color_bar_3d = None

        self.plot_3d = ImagePlot(parent=self)
        self.plot_2d = ImagePlot(parent=self)
        self.plot_1d = LinePlot(parent=self)
        self.controller = ImageToolController(parent=self)
        
        self.plot_3d_dock = Dock(
            name="3D Image Plot",
            size=(10, 10),
            widget=self.plot_3d,
            hideTitle=True,
            closable=False
        )
        self.plot_2d_dock = Dock(
            name="2D Image Plot",
            size=(10, 10),
            widget=self.plot_2d,
            hideTitle=True,
            closable=False
        )
        self.plot_1d_dock = Dock(
            name="Line Plot",
            size=(10, 10),
            widget=self.plot_1d,
            hideTitle=True,
            closable=False
        )
        self.controller_dock = Dock(
            name="Color Mapping",
            size=(10, 1),
            widget=self.controller,
            hideTitle=True,
            closable=False
        )
        self.addDock(self.controller_dock)
        self.addDock(self.plot_3d_dock, "left", self.controller_dock)
        self.addDock(self.plot_2d_dock, "bottom", self.plot_3d_dock)
        self.addDock(self.plot_1d_dock, "bottom", self.plot_2d_dock)
        self.controller_dock.setMaximumWidth(200)
        self.controller_dock.setMinimumWidth(200)

        # If ROI is activated, proper dock will show
        self.plot_2d_dock.hide()
        self.plot_1d_dock.hide()

    def _setImage(
        self,
        image: np.ndarray,
        data: np.ndarray,
        x_label: str=None,
        y_label: str=None,
        x_coords: list=None,
        y_coords: list=None
    ):
        
        if self.data is None:
            self.data = data
            self.data_min, self.data_max = np.amin(data), np.amax(data)
            
            image = np.copy(image)
            image[image > self.color_map_max] = self.data_max
            image = image / self.data_max

            self.plot_3d._setLabels(x=x_label, y=y_label)
            self.plot_3d._setImage(image=image)
            self.plot_3d._setCoordinates(x=x_coords, y=y_coords)
            self.plot_3d._setImage(image=image)
            self.plot_3d._setCoordinates(x=x_coords, y=y_coords)

            self.controller._setColorMap()
        else:
            image = np.copy(image)
            image[image > self.color_map_max] = self.color_map_max
            image = image / self.color_map_max

            self.plot_3d._setLabels(x=x_label, y=y_label)
            self.plot_3d._setImage(image=image)
            self.plot_3d._setCoordinates(x=x_coords, y=y_coords)

            self.color_bar_3d.setLevels((0, self.color_map_max))


    def _setColorMap(self, color_map):
        self.plot_3d.setColorMap(color_map)

        if self.color_bar_3d is not None:
            self.color_bar_3d.setCmap(color_map)
        else:
            self.color_bar_3d = pg.ColorBarItem(
                values=(0, self.color_map_max),
                cmap=color_map,
                interactive=False,
                width=15,
                orientation="h"
            )
            self.color_bar_3d.setImageItem(
                img=self.plot_3d.image,
                insert_in=self.plot_3d.getView()
            )
        
    def _getMouseCoordinates(self, x, y):

        from imageanalysis.ui.data_view.gridded_data import GriddedDataWidget
        from imageanalysis.ui.data_view.raw_data import RawDataWidget
        
        h, k, l, value = None, None, None, None
        if x is not None:
            if type(self.parent) == RawDataWidget:
                i = self.parent.controller.slice_index
                h, k, l = self.parent.scan.rsm[i, x, y]
                value = self.parent.scan.raw_image_data[i, x, y]
            elif type(self.parent) == GriddedDataWidget:
                dim_order = self.parent.controller.dim_order
                data = np.transpose(self.data, dim_order)
                i = self.parent.controller.slice_index
                value = data[x, y, i]
                h = self.parent.scan.gridded_image_coords[0][[x, y, i][dim_order.index(0)]]
                k = self.parent.scan.gridded_image_coords[1][[x, y, i][dim_order.index(1)]]
                l = self.parent.scan.gridded_image_coords[2][[x, y, i][dim_order.index(2)]]
          
        self.controller._setMouseInfo(h=h, k=k, l=l, value=value)

    def _setColorMapMax(self):
        self.color_map_max = self.controller.color_map_ctrl.color_map_max
        self.parent.controller._setImage()


class ImageToolController(QtGui.QWidget):

    def __init__(self, parent) -> None:
        super().__init__()

        self.image_tool = parent

        self.mouse_info_widget = MouseInfoWidget()
        self.color_map_ctrl = ColorMapController(parent=self)

        self.layout = QtGui.QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.mouse_info_widget)
        self.layout.addWidget(self.color_map_ctrl)

        self.color_map_ctrl.colorMapChanged.connect(self._setColorMap)
        self.color_map_ctrl.colorMapBoundsChanged.connect(self.image_tool._setColorMapMax)

    def _setMouseInfo(self, h, k, l, value):
        # Calls mouse info
        self.mouse_info_widget._updateMouseInfo(h, k, l, value)

    def _setColorMap(self):
        color_map = self.color_map_ctrl.color_map
        self.image_tool._setColorMap(color_map=color_map)

class ImagePlot(pg.ImageView):

    def __init__(self, parent) -> None:
        super(ImagePlot, self).__init__(
            imageItem=pg.ImageItem(),
            view=pg.PlotItem()
        )

        self.image_tool = parent
        self.image = None
        self.transform = None
        self.x_coords, self.y_coords = None, None

        self.ui.histogram.hide()
        self.ui.roiBtn.hide()
        self.ui.menuBtn.hide()
        self.getView().setAspectLocked(False)
        self.getView().ctrlMenu = None

        self.getView().scene().sigMouseMoved.connect(self._getMouseInfo)

    def _setImage(self, image: np.ndarray):
        self.image = image

        self.setImage(
            img=self.image,
            autoRange=False,
            autoLevels=False,
            transform=self.transform
        )
    
    def _setLabels(self, x: str=None, y: str=None) -> None:
        if x is not None and type(x) == str:
            self.getView().setLabel("bottom", x)
        if y is not None and type(y) == str:
            self.getView().setLabel("left", y)

    def _setCoordinates(self, x=None, y=None):
        if self.image is not None:
            self.transform = QtGui.QTransform()

            if x is None:
                x = np.linspace(
                    start=0, 
                    stop=self.image.shape[0] - 1, 
                    num=self.image.shape[0],
                    endpoint=False
                )

            if y is None:
                y = np.linspace(
                    start=0, 
                    stop=self.image.shape[1] - 1, 
                    num=self.image.shape[1],
                    endpoint=False
                )

            scale = (x[1] - x[0], y[1] - y[0])
            pos = (x[0], y[0])
            self.transform.translate(*pos)
            self.transform.scale(*scale)
            self.x_coords, self.y_coords = x, y
        else:
            self.transform = None

    def _getMouseInfo(self, scene_point=None):
        
        if scene_point is not None:
            view_point = self.getView().vb.mapSceneToView(scene_point)
            x = int(self.image.shape[0] * ((view_point.x() - self.x_coords[0]) / (self.x_coords[-1] - self.x_coords[0])))
            y = int(self.image.shape[1] * ((view_point.y() - self.y_coords[0]) / (self.y_coords[-1] - self.y_coords[0])))
            if 0 <= x < self.image.shape[0] and 0 <= y < self.image.shape[1]:
                self.image_tool._getMouseCoordinates(x, y)
            else:
                self.image_tool._getMouseCoordinates(None, None)

class LinePlot(pg.PlotWidget):

    def __init__(self, parent) -> None:
        super().__init__()

        self.image_tool = parent

    def _setData():
        ...

    def _setLabels():
        ...

class MouseInfoWidget(QtGui.QGroupBox):

    def __init__(self) -> None:
        super().__init__()

        self.h_lbl, self.h_txt = QtGui.QLabel("H: "), QtGui.QLineEdit()
        self.h_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.k_lbl, self.k_txt = QtGui.QLabel("K: "), QtGui.QLineEdit()
        self.k_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.l_lbl, self.l_txt = QtGui.QLabel("L: "), QtGui.QLineEdit()
        self.l_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.value_lbl = QtGui.QLabel("Value: ")
        self.value_lbl.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter
        )
        self.value_txt = QtGui.QLineEdit()

        self.layout = QtGui.QGridLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.h_lbl, 0, 0)
        self.layout.addWidget(self.h_txt, 0, 1, 1, 5)
        self.layout.addWidget(self.k_lbl, 1, 0)
        self.layout.addWidget(self.k_txt, 1, 1, 1, 5)
        self.layout.addWidget(self.l_lbl, 2, 0)
        self.layout.addWidget(self.l_txt, 2, 1, 1, 5)
        self.layout.addWidget(self.value_lbl, 3, 0)
        self.layout.addWidget(self.value_txt, 3, 1, 1, 5)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)
        self.layout.setColumnStretch(3, 1)
        self.layout.setColumnStretch(4, 1)
        self.layout.setColumnStretch(5, 1)

    def _updateMouseInfo(self, h=None, k=None, l=None, value=None):
        if h is not None:
            self.h_txt.setText(str(round(h, 7)))
            self.k_txt.setText(str(round(k, 7)))
            self.l_txt.setText(str(round(l, 7) or ""))
            self.value_txt.setText(str(round(value, 3)))
        else:
            self.h_txt.setText("")
            self.k_txt.setText("")
            self.l_txt.setText("")
            self.value_txt.setText("")