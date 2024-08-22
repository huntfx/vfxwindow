from __future__ import absolute_import

import sys

import Qt


def bypassWebEngine():
    """Blender 4.2 introducted a crash on import on Windows machines.
    Bypassing the QWebEngine components solves it.
    https://community.shotgridsoftware.com/t/shotgrid-with-tk-blender/17217/11
    """
    # PySide6 support added in Qt 1.4.1
    isPySide6 = getattr(Qt, 'IsPySide6', False)
    if not isPySide6 or sys.platform != 'win32':
        return

    # Override QtWebEngine for both Qt and PySide6
    # PySide6 is included here just to fix it for other scripts
    import PySide6
    class QtWebEngineCore:
        QWebEnginePage = None
        QWebEngineProfile = None
    Qt.QtWebEngineCore = PySide6.QtWebEngineCore = QtWebEngineCore
    Qt.QtWebEngineWidgets = PySide6.QtWebEngineWidgets = None
