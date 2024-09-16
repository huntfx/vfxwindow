"""Test features to make sure they work for specific programs."""

from __future__ import absolute_import, print_function

import os
import random
import sys
from Qt import QtWidgets

sys.path.append(os.path.abspath(__file__).rsplit(os.path.sep, 2)[0])
from vfxwindow import VFXWindow
from vfxwindow.utils.palette import getPaletteList


class Window(VFXWindow):
    WindowID = 'test_functionality'
    def __init__(self, parent=None, **kwargs):
        super(Window, self).__init__(parent, **kwargs)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        container.setLayout(layout)
        self.setCentralWidget(container)

        paletteButton = QtWidgets.QPushButton('Random Palette')
        paletteButton.clicked.connect(self.palette)
        layout.addWidget(paletteButton)


    def palette(self):
        newPalette = random.choice(getPaletteList())
        self.setWindowPalette(*newPalette.split('.', 1))
        print('Switched palette to {} (expected: {})'.format(self.windowPalette(), newPalette))


if __name__ == '__main__':
    Window.show()
