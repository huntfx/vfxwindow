from Qt import QtCore, QtWidgets
from . import VFXWindow


class TestWindow(VFXWindow):
    WindowID = 'vfxwindow.debug'
    WindowName = 'VFXWindow Debug'
    WindowDockable = True

    def __init__(self, **kwargs):
        self._signalPause = False
        super(TestWindow, self).__init__(**kwargs)
        self.setWindowIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DirIcon))

        widget = QtWidgets.QWidget()
        self.setCentralWidget(widget)

        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)

        grid = QtWidgets.QGridLayout()
        layout.addLayout(grid)

        grid.addWidget(QtWidgets.QLabel('Position:'), 0, 0)
        self.xPos = QtWidgets.QSpinBox()
        self.xPos.setRange(-2 ** 16, 2 ** 16)
        self.xPos.setSingleStep(10)
        self.yPos = QtWidgets.QSpinBox()
        self.yPos.setRange(-2 ** 16, 2 ** 16)
        self.yPos.setSingleStep(10)
        posLayout = QtWidgets.QHBoxLayout()
        posLayout.addWidget(self.xPos)
        posLayout.addWidget(self.yPos)
        grid.addLayout(posLayout, 0, 1)

        grid.addWidget(QtWidgets.QLabel('Size:'), 1, 0)
        self.wVal = QtWidgets.QSpinBox()
        self.wVal.setRange(0, 2 ** 16)
        self.wVal.setSingleStep(4)
        self.hVal = QtWidgets.QSpinBox()
        self.hVal.setRange(0, 2 ** 16)
        self.hVal.setSingleStep(4)
        sizeLayout = QtWidgets.QHBoxLayout()
        sizeLayout.addWidget(self.wVal)
        sizeLayout.addWidget(self.hVal)
        grid.addLayout(sizeLayout, 1, 1)

        grid.addWidget(QtWidgets.QLabel('Floating:'), 2, 0)
        self.floatingChk = QtWidgets.QCheckBox()
        grid.addWidget(self.floatingChk, 2, 1)

        grid.addWidget(QtWidgets.QLabel('Visible:'), 3, 0)
        self.visibleChk = QtWidgets.QCheckBox()
        grid.addWidget(self.visibleChk, 3, 1)

        layout.addStretch()

        refreshAll = QtWidgets.QPushButton('Refresh All')
        layout.addWidget(refreshAll)

        self.windowReady.connect(self.refresh)
        refreshAll.clicked.connect(self.refresh)
        self.xPos.valueChanged.connect(self.moveRequested)
        self.yPos.valueChanged.connect(self.moveRequested)
        self.wVal.valueChanged.connect(self.resizeRequested)
        self.hVal.valueChanged.connect(self.resizeRequested)
        self.floatingChk.stateChanged.connect(self.toggleFloating)
        self.visibleChk.stateChanged.connect(self.toggleVisible)

    @QtCore.Slot()
    def refresh(self):
        self._signalPause = True
        try:
            self.xPos.setValue(self.x())
            self.yPos.setValue(self.y())
            self.wVal.setValue(self.width())
            self.hVal.setValue(self.height())
            self.floatingChk.setChecked(self.floating())
            self.visibleChk.setChecked(self.isVisible())
        finally:
            self._signalPause = False

    @QtCore.Slot()
    def moveRequested(self):
        if self._signalPause:
            return
        self.move(self.xPos.value(), self.yPos.value())

    @QtCore.Slot()
    def resizeRequested(self):
        if self._signalPause:
            return
        self.resize(self.wVal.value(), self.hVal.value())

    @QtCore.Slot(int)
    def toggleFloating(self, checkState):
        if self._signalPause:
            return
        self.setFloating(checkState == QtCore.Qt.Checked)

    @QtCore.Slot(int)
    def toggleVisible(self, checkState):
        if self._signalPause:
            return
        self.setVisible(checkState == QtCore.Qt.Checked)

    @classmethod
    def clearWindowInstance(cls, *args, **kwargs):
        print('clearWindowInstance')
        return super(TestWindow, cls).clearWindowInstance(*args, **kwargs)

    def closeEvent(self, *args, **kwargs):
        print('closeEvent')
        return super(TestWindow, self).closeEvent(*args, **kwargs)

    def eventFilter(self, obj, event):
        print('eventFilter on {}: {}'.format(obj, event.type()))
        return super(TestWindow, self).eventFilter(obj, event)


def main():
    return TestWindow.show()


if __name__ == '__main__':
    main()
