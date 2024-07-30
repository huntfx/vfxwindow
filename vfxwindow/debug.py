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
            self.callbacks.add('file.new.before', lambda clientData: self.callbacks['pauseOnNew'].unregister())
            self.callbacks.add('file.new.after', lambda clientData: self.callbacks['pauseOnNew'].register())
            self.callbacks.add('file.open.before', lambda clientData: self.callbacks['pauseOnNew'].unregister())
            self.callbacks.add('file.open.after', lambda clientData: self.callbacks['pauseOnNew'].register())

        # Add test callbacks
        if self.application == 'Maya':
            import maya.cmds as mc
            import maya.api.OpenMaya as om2
            self.callbacks.add('file.new', lambda clientData: print('Callback: file.new'))
            self.callbacks.add('file.new.before', lambda clientData: print('Callback: file.new.before'))
            def beforeNewCheck(clientData):
                print('Callback: file.new.before.check')
                return True
            self.callbacks.add('file.new.before.check', beforeNewCheck)
            self.callbacks.add('file.new.after', lambda clientData: print('Callback: file.new.after'))
            self.callbacks.add('file.load', lambda clientData: print('Callback: file.load'))
            self.callbacks.add('file.load.before', lambda clientData: print('Callback: file.load.before'))
            def beforeOpenCheck(fileObj, clientData):
                print('Callback: file.load.before.check ({})'.format(fileObj.resolvedFullName()))
                return True
            self.callbacks.add('file.load.before.check', beforeOpenCheck)
            self.callbacks.add('file.load.after', lambda clientData: print('Callback: file.load.after'))
            self.callbacks.add('file.save', lambda clientData: print('Callback: file.save'))
            self.callbacks.add('file.save.before', lambda clientData: print('Callback: file.save.before'))
            def beforeSaveCheck(clientData):
                print('Callback: file.save.before.check')
                return True
            self.callbacks.add('file.save.before.check', beforeSaveCheck)
            self.callbacks.add('file.save.after', lambda clientData: print('Callback: file.save.after'))
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
            self.callbacks.add('app.start', lambda clientData: print('Callback: app.init'))
            self.callbacks.add('app.exit', lambda clientData: print('Callback: app.exit'))
            self.callbacks.add('plugin.load', lambda data, clientData: print('Callback: plugin.load ({})'.format(data)))
            self.callbacks.add('plugin.load.before', lambda data, clientData: print('Callback: plugin.load.before ({})'.format(data)))
            self.callbacks.add('plugin.load.after', lambda data, clientData: print('Callback: plugin.load.after ({})'.format(data)))
            self.callbacks.add('plugin.unload', lambda data, clientData: print('Callback: plugin.unload ({})'.format(data)))
            self.callbacks.add('plugin.unload.before', lambda data, clientData: print('Callback: plugin.unload.before ({})'.format(data)))
            self.callbacks.add('plugin.unload.after', lambda data, clientData: print('Callback: plugin.unload.after ({})'.format(data)))
            self.callbacks['pauseOnNew'].add('connection', lambda srcPlug, dstPlug, made, clientData: print('Callback: connection ({}, {}, {})'.format(srcPlug, dstPlug, made)))
            self.callbacks['pauseOnNew'].add('connection.before', lambda srcPlug, dstPlug, made, clientData: print('Callback: connection.before ({}, {}, {})'.format(srcPlug, dstPlug, made)))
            self.callbacks['pauseOnNew'].add('connection.after', lambda srcPlug, dstPlug, made, clientData: print('Callback: connection.after ({}, {}, {})'.format(srcPlug, dstPlug, made)))
            self.callbacks['pauseOnNew'].add('frame.changed', lambda time, clientData: print('Callback: frame.changed: ({})'.format(time.value)))
            self.callbacks['pauseOnNew'].add('frame.changed.after', lambda time, clientData: print('Callback: frame.changed.deferred: ({})'.format(time.value)))
            self.callbacks.add('node.added', lambda node, clientData: print('Callback: node.added ({})'.format(node)), nodeType='dependNode')
            self.callbacks.add('node.removed', lambda node, clientData: print('Callback: node.removed ({})'.format(node)), nodeType='dependNode')
            self.callbacks.add('node.rename', lambda node, prevName, clientData: print('Callback: node.renamed ({}, {})'.format(node, prevName)), om2.MObject.kNullObj)
            self.callbacks.add('node.uuid.set', lambda node, prevUuid, clientData: print('Callback: node.uuid.set ({}, {})'.format(node, prevUuid)), om2.MObject.kNullObj)
            self.callbacks.add('node.dirty', lambda node, clientData: print('Callback: node.dirty ({})'.format(node)), om2.MObject.kNullObj)
            self.callbacks.add('node.dirty.plug', lambda node, plug, clientData: print('Callback: node.dirty.plug ({})'.format(node, plug)), om2.MObject.kNullObj)
            self.callbacks.add('node.destroyed', lambda clientData: print('Callback: destroyed'), om2.MObject.kNullObj)
            self.callbacks.add('attribute.changed', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.changed ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.added', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.added ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.removed', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.removed ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.rename', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.renamed ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.value', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.value ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.value.changed', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.value.changed ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.locked', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.locked ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.locked.set', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.locked.set ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.locked.unset', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.locked.unset ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.keyable', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.keyable ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.keyable.set', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.keyable.set ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)
            self.callbacks.add('attribute.keyable.unset', lambda msg, plug, otherPlug, clientData: print('Callback: attribute.keyable.unset ({}, {}, {})'.format(msg, plug, otherPlug)), om2.MObject.kNullObj)

            if mc.objExists('pCube1'):
                selection = om2.MSelectionList()
                selection.add('pCube1.translateX')
                def keyableChangeOverride(plug, clientData, msg):
                    print('attribute.keyable.override ({}, {})'.format(plug, msg))
                    return True
                self.callbacks.add('attribute.keyable.override', keyableChangeOverride, selection.getPlug(0))


        elif self.application == 'Nuke':
            import nuke
            self.callbacks.add('file.new', lambda: print('Callback: file.new ({})'.format(self._nukeThisNode())))
            self.callbacks.add('file.load', lambda: print('Callback: file.load ({})'.format(self._nukeThisNode())))
            self.callbacks.add('file.save', lambda: print('Callback: file.save ({})'.format(self._nukeThisNode())))
            self.callbacks.add('file.close', lambda: print('Callback: file.close ({})'.format(self._nukeThisNode())))
            self.callbacks.add('node.added', lambda: print('Callback: node.added ({})'.format(self._nukeThisNode())))
            self.callbacks.add('node.added.user', lambda: print('Callback: node.added.user ({})'.format(self._nukeThisNode())))
            self.callbacks.add('node.removed', lambda: print('Callback: node.removed ({})'.format(self._nukeThisNode())))
            self.callbacks.add('knob.changed', lambda: print('Callback: knob.changed ({}, {})'.format(self._nukeThisNode(), self._nukeThisKnob())))
            self.callbacks.add('ui.update', lambda: print('Callback: ui.update ({})'.format(self._nukeThisNode())))

            self.callbacks.add('render', lambda: print('Callback: render ({})'.format(self._nukeThisNode())))
            self.callbacks.add('render.before', lambda: print('Callback: render.before ({})'.format(self._nukeThisNode())))
            self.callbacks.add('render.after', lambda: print('Callback: render.after ({})'.format(self._nukeThisNode())))
            self.callbacks.add('render.frame', lambda: print('Callback: render.frame ({})'.format(self._nukeThisNode())))
            self.callbacks.add('render.frame.before', lambda: print('Callback: render.frame.before ({})'.format(self._nukeThisNode())))
            self.callbacks.add('render.frame.after', lambda: print('Callback: render.frame.after ({})'.format(self._nukeThisNode())))
            self.callbacks.add('render.background', lambda: print('Callback: render.background'))
            self.callbacks.add('render.background.after', lambda: print('Callback: render.background.after'))
            self.callbacks.add('render.background.frame', lambda: print('Callback: render.background.frame'))
            self.callbacks.add('render.background.frame.after', lambda: print('Callback: render.background.frame.after'))

        elif self.application == 'Blender':
            from bpy.app.handlers import persistent
            self.callbacks.add('file.load', persistent(lambda path, _: print('Callback: file.load ({})'.format(path))))
            self.callbacks.add('file.load.before', persistent(lambda path, _: print('Callback: file.load.before ({})'.format(path))))
            self.callbacks.add('file.load.after', persistent(lambda path, _: print('Callback: file.load.after ({})'.format(path))))
            self.callbacks.add('file.load.fail', persistent(lambda path, _: print('Callback: file.load.fail ({})'.format(path))))
            self.callbacks.add('file.save', persistent(lambda path, _: print('Callback: file.save ({})'.format(path))))
            self.callbacks.add('file.save.before', persistent(lambda path, _: print('Callback: file.save.before ({})'.format(path))))
            self.callbacks.add('file.save.after', persistent(lambda path, _: print('Callback: file.save.after ({})'.format(path))))
            self.callbacks.add('file.save.fail', persistent(lambda path, _: print('Callback: file.save.fail ({})'.format(path))))
            self.callbacks.add('render', persistent(lambda scene, _: print('Callback: render ({})'.format(scene.name))))
            self.callbacks.add('render.cancel', persistent(lambda scene, _: print('Callback: render.cancel ({})'.format(scene.name))))
            self.callbacks.add('render.before', persistent(lambda scene, _: print('Callback: render.before ({})'.format(scene.name))))
            self.callbacks.add('render.after', persistent(lambda scene, _: print('Callback: render.after ({})'.format(scene.name))))
            self.callbacks.add('render.frame.before', persistent(lambda scene, _: print('Callback: render.frame.before ({})'.format(scene.name))))
            self.callbacks.add('render.frame.after', persistent(lambda scene, _: print('Callback: render.frame.after ({})'.format(scene.name))))
            self.callbacks.add('render.frame.write', persistent(lambda scene, _: print('Callback: render.frame.write ({})'.format(scene.name))))
            self.callbacks.add('undo', persistent(lambda scene, _: print('Callback: undo ({})'.format(scene.name))))
            self.callbacks.add('undo.before', persistent(lambda scene, _: print('Callback: undo.before ({})'.format(scene.name))))
            self.callbacks.add('undo.after', persistent(lambda scene, _: print('Callback: undo.after ({})'.format(scene.name))))
            self.callbacks.add('redo', persistent(lambda scene, _: print('Callback: redo ({})'.format(scene.name))))
            self.callbacks.add('redo.before', persistent(lambda scene, _: print('Callback: redo.before ({})'.format(scene.name))))
            self.callbacks.add('redo.after', persistent(lambda scene, _: print('Callback: redo.after ({})'.format(scene.name))))
            self.callbacks.add('frame.changed', persistent(lambda scene, _: print('Callback: frame.changed ({})'.format(scene.name))))
            self.callbacks.add('frame.changed.before', persistent(lambda scene, _: print('Callback: frame.changed.before ({})'.format(scene.name))))
            self.callbacks.add('frame.changed.after', persistent(lambda scene, depsgraph: print('Callback: frame.changed.after ({})'.format(scene.name))))
            self.callbacks.add('frame.playback', persistent(lambda scene, depsgraph: print('Callback: frame.playback ({})'.format(scene.name))))
            self.callbacks.add('frame.playback.before', persistent(lambda scene, depsgraph: print('Callback: frame.playback.before ({})'.format(scene.name))))
            self.callbacks.add('frame.playback.after', persistent(lambda scene, depsgraph: print('Callback: frame.playback.after ({})'.format(scene.name))))

            self.callbacks.add('undo', lambda scene, _: print('Callback: redo non-persistent ({})'.format(scene.name)))
            self.callbacks.add('redo', lambda scene, _: print('Callback: redo non-persistent ({})'.format(scene.name)))

        elif self.application == 'Substance Designer':
            self.callbacks.add('file.load', lambda explorerID: print('file.load (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('file.load.before', lambda explorerID: print('file.load.before (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('file.load.after', lambda explorerID: print('file.load.after (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('file.save', lambda explorerID: print('file.save (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('file.save.before', lambda explorerID: print('file.save.before (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('file.save.after', lambda explorerID: print('file.save.after (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('file.close', lambda explorerID: print('file.close (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('file.close.before', lambda explorerID: print('file.close.before (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('file.close.after', lambda explorerID: print('file.close.after (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('ui.graph.created', lambda graphViewID: print('graph.created (graphViewID={!r})'.format(graphViewID)))
            self.callbacks.add('ui.explorer.created', lambda explorerID: print('explorer.created (explorerID={!r})'.format(explorerID)))
            self.callbacks.add('ui.explorer.selection.changed', lambda explorerID: print('explorer.selection.changed (explorerID={!r})'.format(explorerID)))

        elif self.application == 'Substance Painter':
            self.callbacks.add('file.load', lambda evt: print('file.load'))
            self.callbacks.add('file.new', lambda evt: print('file.new'))
            self.callbacks.add('file.close', lambda evt: print('file.close'))
            self.callbacks.add('file.close.before', lambda evt: print('file.close.before'))
            self.callbacks.add('file.save', lambda evt: print('file.save'))
            self.callbacks.add('file.save.before', lambda evt: print('file.save.before (file_path={!r})'.format(evt.file_path)))
            self.callbacks.add('file.save.after', lambda evt: print('file.save'))
            self.callbacks.add('export.textures.before', lambda evt: print('file.new (textures={!r})'.format(evt.textures)))
            self.callbacks.add('export.textures.after', lambda evt: print('file.new (message={!r}, status={!r}, textures={!r})'.format(evt.message, evt.status, evt.textures)))
            self.callbacks.add('shelf.crawling', lambda evt: print('shelf.crawling (shelf_name={!r})'.format(evt.shelf_name)))
            self.callbacks.add('shelf.crawling.before', lambda evt: print('shelf.crawling.before (shelf_name={!r})'.format(evt.shelf_name)))
            self.callbacks.add('shelf.crawling.after', lambda evt: print('shelf.crawling.after (shelf_name={!r})'.format(evt.shelf_name)))

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

    def _nukeThisNode(self):
        import nuke
        node = nuke.thisNode()
        if node is None or not isinstance(node, nuke.Node):
            return None
        return node.name() or 'Root'

    def _nukeThisKnob(self):
        import nuke
        knob = nuke.thisKnob()
        if knob is None:
            return None
        return knob.name()

def main():
    return TestWindow.show()


if __name__ == '__main__':
    main()
