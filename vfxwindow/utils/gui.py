from __future__ import absolute_import

from Qt import QtWidgets


def forceMenuBar(win):
    """Force add the menuBar if it is not there by default.
    In Maya this is needed for docked windows.

    Each menuBar appears to contain a QToolButton and then the menus,
    so check how many children
    This only works with .insertWidget() - creating a new layout and
    adding both widgets won't do anything.
    """
    menu = win.menuBar()
    if not menu.actions():
        for child in menu.children():
            if isinstance(child, QtWidgets.QMenu):
                break
        else:
            return
    menu.setSizePolicy(menu.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Fixed)
    win.centralWidget().layout().insertWidget(0, menu)
