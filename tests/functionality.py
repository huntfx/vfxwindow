"""Test features to make sure they work for specific programs."""

import os
import random
import sys
sys.path.append(os.path.abspath(__file__).rsplit(os.path.sep, 2)[0])

from vfxwindow import VFXWindow
from vfxwindow.palette import getPaletteList
from vfxwindow.utils.Qt import QtWidgets


class Window(VFXWindow):
    def __init__(self, parent=None, **kwargs):
        super(Window, self).__init__(parent, **kwargs)

        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        container.setLayout(layout)
        self.setCentralWidget(container)

        messageButton = QtWidgets.QPushButton('Popup Message')
        messageButton.clicked.connect(self.message)
        layout.addWidget(messageButton)

        confirmButton = QtWidgets.QPushButton('Confirmation Box')
        confirmButton.clicked.connect(self.confirm)
        layout.addWidget(confirmButton)

        paletteButton = QtWidgets.QPushButton('Random Palette')
        paletteButton.clicked.connect(self.palette)
        layout.addWidget(paletteButton)

    def message(self):
        """Test message box."""
        value = self.displayMessage(
            title='Test',
            message='This is a test.'
        )
        print('Chosen value: {}'.format(value))
        return value
    
    def confirm(self):
        """Test confirmation box."""
        value = self.displayMessage(
            title='Test',
            message='This is a test.',
            buttons=('Yes', 'No'),
            defaultButton='Yes',
            cancelButton='No',
        )
        print('Chosen value: {}'.format(value))
        return value

    def palette(self):
        newPalette = random.choice(getPaletteList())
        self.setWindowPalette(*newPalette.split('.', 1))
        print('Switched palette to {} (expected: {})'.format(self.windowPalette(), newPalette))


if __name__ == '__main__':
    Window.show()
