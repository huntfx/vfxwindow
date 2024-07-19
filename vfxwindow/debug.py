from __future__ import absolute_import, print_function

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

        menu = self.menuBar().addMenu('File')
        menu.addAction('Exit', self.close)

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

        # Add legit callbacks
        if self.application == 'Maya':
            self.callbacks.add('new.before', lambda clientData: self.callbacks['pauseOnNew'].unregister())
            self.callbacks.add('new.after', lambda clientData: self.callbacks['pauseOnNew'].register())
            self.callbacks.add('open.before', lambda clientData: self.callbacks['pauseOnNew'].unregister())
            self.callbacks.add('open.after', lambda clientData: self.callbacks['pauseOnNew'].register())

        # Add test callbacks
        if self.application == 'Maya':
            self.callbacks.add('new', lambda clientData: print('Callback: new'))
            self.callbacks.add('new.before', lambda clientData: print('Callback: new.before'))
            self.callbacks.add('new.after', lambda clientData: print('Callback: new.after'))
            self.callbacks.add('open', lambda clientData: print('Callback: open'))
            self.callbacks.add('open.before', lambda clientData: print('Callback: open.before'))
            def beforeOpenCheck(fileObj, clientData):
                print('Callback: open.before.check ({})'.format(fileObj.resolvedFullName()))
                return True
            self.callbacks.add('open.before.check', beforeOpenCheck)
            self.callbacks.add('open.after', lambda clientData: print('Callback: open.after'))
            self.callbacks.add('save', lambda clientData: print('Callback: save'))
            self.callbacks.add('save.before', lambda clientData: print('Callback: save.before'))
            def beforeSaveCheck(clientData):
                print('Callback: save.before.check')
                return True
            self.callbacks.add('save.before.check', beforeSaveCheck)
            self.callbacks.add('save.after', lambda clientData: print('Callback: save.after'))
            self.callbacks.add('import', lambda clientData: print('Callback: import'))
            self.callbacks.add('import.before', lambda clientData: print('Callback: import.before'))
            def beforeImportCheck(fileObj, clientData):
                print('Callback: import.before.check ({})'.format(fileObj.resolvedFullName()))
                return True
            self.callbacks.add('import.before.check', beforeImportCheck)
            self.callbacks.add('import.after', lambda clientData: print('Callback: import.after'))
            self.callbacks.add('reference', lambda clientData: print('Callback: reference'))
            self.callbacks.add('reference.create', lambda clientData: print('Callback: reference.create'))
            self.callbacks.add('reference.create.before', lambda clientData: print('Callback: reference.create.before'))
            def beforeRefCreateCheck(fileObj, clientData):
                print('Callback: reference.create.before.check ({})'.format(fileObj.resolvedFullName()))
                return True
            self.callbacks.add('reference.create.before.check', beforeRefCreateCheck)
            self.callbacks.add('reference.create.after', lambda clientData: print('Callback: reference.create.after'))
            self.callbacks.add('reference.remove', lambda clientData: print('Callback: reference.remove'))
            self.callbacks.add('reference.remove.before', lambda clientData: print('Callback: reference.remove.before'))
            self.callbacks.add('reference.remove.after', lambda clientData: print('Callback: reference.remove.after'))
            self.callbacks.add('reference.load', lambda clientData: print('Callback: reference.load'))
            self.callbacks.add('reference.load.before', lambda clientData: print('Callback: reference.load.before'))
            def beforeRefLoadCheck(fileObj, clientData):
                print('Callback: reference.load.before.check ({})'.format(fileObj.resolvedFullName()))
                return True
            self.callbacks.add('reference.load.before.check', beforeRefLoadCheck)
            self.callbacks.add('reference.load.after', lambda clientData: print('Callback: reference.load.after'))
            self.callbacks.add('reference.unload', lambda clientData: print('Callback: reference.unload'))
            self.callbacks.add('reference.unload.before', lambda clientData: print('Callback: reference.unload.before'))
            self.callbacks.add('reference.unload.after', lambda clientData: print('Callback: reference.unload.after'))
            self.callbacks.add('reference.import', lambda clientData: print('Callback: reference.import'))
            self.callbacks.add('reference.import.before', lambda clientData: print('Callback: reference.import.before'))
            self.callbacks.add('reference.import.after', lambda clientData: print('Callback: reference.import.after'))
            self.callbacks.add('reference.export', lambda clientData: print('Callback: reference.export'))
            self.callbacks.add('reference.export.before', lambda clientData: print('Callback: reference.export.before'))
            self.callbacks.add('reference.export.after', lambda clientData: print('Callback: reference.export.after'))
            self.callbacks.add('render', lambda clientData: print('Callback: render'))
            self.callbacks.add('render.software', lambda clientData: print('Callback: render.software'))
            self.callbacks.add('render.software.before', lambda clientData: print('Callback: render.software.before'))
            self.callbacks.add('render.software.after', lambda clientData: print('Callback: render.software.after'))
            self.callbacks.add('render.software.frame', lambda clientData: print('Callback: render.software.frame'))
            self.callbacks.add('render.software.frame.before', lambda clientData: print('Callback: render.software.frame.before'))
            self.callbacks.add('render.software.frame.after', lambda clientData: print('Callback: render.software.frame.after'))
            self.callbacks.add('render.software.interrupted', lambda clientData: print('Callback: render.software.interrupted'))
            self.callbacks.add('application.start', lambda clientData: print('Callback: application.start'))
            self.callbacks.add('application.exit', lambda clientData: print('Callback: application.exit'))
            self.callbacks.add('plugin.load', lambda data, clientData: print('Callback: plugin.load ({})'.format(data)))
            self.callbacks.add('plugin.load.before', lambda data, clientData: print('Callback: plugin.load.before ({})'.format(data)))
            self.callbacks.add('plugin.load.after', lambda data, clientData: print('Callback: plugin.load.after ({})'.format(data)))
            self.callbacks.add('plugin.unload', lambda data, clientData: print('Callback: plugin.unload ({})'.format(data)))
            self.callbacks.add('plugin.unload.before', lambda data, clientData: print('Callback: plugin.unload.before ({})'.format(data)))
            self.callbacks.add('plugin.unload.after', lambda data, clientData: print('Callback: plugin.unload.after ({})'.format(data)))
            self.callbacks['pauseOnNew'].add('connection', lambda srcPlug, dstPlug, made, clientData: print('Callback: connection ({}, {}, {})'.format(srcPlug, dstPlug, made)))
            self.callbacks['pauseOnNew'].add('connection.before', lambda srcPlug, dstPlug, made, clientData: print('Callback: connection.before ({}, {}, {})'.format(srcPlug, dstPlug, made)))
            self.callbacks['pauseOnNew'].add('connection.after', lambda srcPlug, dstPlug, made, clientData: print('Callback: connection.after ({}, {}, {})'.format(srcPlug, dstPlug, made)))
            # self.callbacks.add('node.added', lambda node, clientData: print('Callback: node.added ({})'.format(node)), nodeType='dependNode')
            # self.callbacks.add('node.removed', lambda node, clientData: print('Callback: node.removed ({})'.format(node)), nodeType='dependNode')
            # self.callbacks.add('node.dirty', lambda node, clientData: print('Callback: node.dirty ({})'.format(node)))
            # self.callbacks.add('node.dirty.plug', lambda node, plug, clientData: print('Callback: node.dirty.plug ({})'.format(node, plug)))
            # self.callbacks.add('node.name.changed', lambda node, prevName, clientData: print('Callback: node.name.changed ({})'.format(node, prevName)))
            # self.callbacks.add('node.uuid.changed', lambda node, prevName, clientData: print('Callback: node.name.changed ({})'.format(node, prevName)))
            # self.callbacks.add('node.destroyed', lambda clientData: print('Callback: destroyed'))
            self.callbacks['pauseOnNew'].add('frame.changed', lambda time, clientData: print('Callback: frame.changed: ({})'.format(time)))
            self.callbacks['pauseOnNew'].add('frame.changed.deferred', lambda time, clientData: print('Callback: frame.changed.deferred: ({})'.format(time)))
            # self.callbacks.add('attribute.changed', lambda msg, plug, clientData: print('Callback: changed.changed ({}, {}, {})'.format(msg, plug)))
            # self.callbacks.add('attribute.value.changed', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.value.changed ({}, {}, {})'.format(msg, plug, otherPlug)))
            # self.callbacks.add('attribute.keyable.changed', lambda plug, clientData: print('Callback: render'))

        # TODO: Add other callbacks
        if self.application == 'Substance Desiger':
            self.addCallbackBeforeFileLoaded(self.substanceDesignerBeforeFileLoad)
            self.addCallbackAfterFileLoaded(self.substanceDesignerAfterFileLoad)
            self.addCallbackBeforeFileSaved(self.substanceDesignerBeforeFileSave)
            self.addCallbackAfterFileSaved(self.substanceDesignerAfterFileSave)
            self.addCallbackBeforeFileClosed(self.substanceDesignerBeforeFileClose)
            self.addCallbackAfterFileClosed(self.substanceDesignerAfterFileClose)

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

    @QtCore.Slot(QtCore.Qt.CheckState)
    def toggleFloating(self, checkState):
        if self._signalPause:
            return
        self.setFloating(checkState == QtCore.Qt.Checked)

    @QtCore.Slot(QtCore.Qt.CheckState)
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

    def substanceDesignerBeforeFileLoad(self, filePath):
        print('Before file load (file: {})'.format(filePath))

    def substanceDesignerAfterFileLoad(self, filePath, succeed, updated):
        print('After file load (file: {}, succeed: {}, updated: {})'.format(filePath, succeed, updated))

    def substanceDesignerBeforeFileSave(self, filePath, parentPackagePath):
        print('Before file saved (file: {}, parentPackage: {})'.format(filePath, parentPackagePath))

    def substanceDesignerAfterFileSave(self, filePath, succeed):
        print('After file saved (file: {}, succeed: {})'.format(filePath, succeed))

    def substanceDesignerBeforeFileClose(self, filePath):
        print('Before file closed (file: {})'.format(filePath))

    def substanceDesignerAfterFileClose(self, filePath, succeed):
        print('After file closed (file: {}, succeed: {})'.format(filePath, succeed))


def main():
    return TestWindow.show()


if __name__ == '__main__':
    main()
