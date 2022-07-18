from pyqtgraph import QtCore
import pytest

from imageanalysis.ui.main_window import MainWindow

# ==================================================================================
@pytest.fixture
def window():
    return MainWindow()

def test_minimum_size(window):
    assert window.minimumSize() == QtCore.QSize(1400, 800)