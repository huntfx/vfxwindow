"""This is a test to see if multiple window instances can be launched.
By default, there can only be one QApplication, so this is an example of launching a second window using a new process.
"""

import sys
import os
from Qt import QtWidgets

sys.path.append(os.path.abspath(__file__).rsplit(os.path.sep, 2)[0])
from vfxwindow import VFXWindow


class Window1(VFXWindow):
    def __init__(self, *args, **kwargs):
        super(Window1, self).__init__(*args, **kwargs)
        self.setCentralWidget(QtWidgets.QPushButton('Open Window'))
        self.centralWidget().clicked.connect(Window2.show)


class Window2(VFXWindow):
    def __init__(self, *args, **kwargs):
        super(Window2, self).__init__(*args, **kwargs)
        self.setCentralWidget(QtWidgets.QPushButton('Close'))
        self.centralWidget().clicked.connect(self.close)


if __name__ == '__main__':
    Window1.show()
