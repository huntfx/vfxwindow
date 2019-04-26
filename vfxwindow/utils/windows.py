from __future__ import absolute_import

import ctypes
import ctypes.wintypes


class RECT(ctypes.Structure):
    _fields_ = [
        ('left', ctypes.c_long),
        ('top', ctypes.c_long),
        ('right', ctypes.c_long),
        ('bottom', ctypes.c_long)
    ]
  
    def dump(self):
        return tuple(map(int, (self.left, self.top, self.right, self.bottom)))


class MONITORINFO(ctypes.Structure):
    _fields_ = [
        ('cbSize', ctypes.c_long),
        ('rcMonitor', RECT),
        ('rcWork', RECT),
        ('dwFlags', ctypes.c_long)
    ]


def _getMonitors():
    """Get a list of all monitors to further processing.
    Source: code.activestate.com/recipes/460509-get-the-actual-and-usable-sizes-of-all-the-monitor
    """
    retval = []
    CBFUNC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong,
                                ctypes.POINTER(RECT), ctypes.c_double)

    def cb(hMonitor, hdcMonitor, lprcMonitor, dwData):
        r = lprcMonitor.contents
        data = [hMonitor]
        data.append(r.dump())
        retval.append(data)
        return 1

    cbfunc = CBFUNC(cb)
    ctypes.windll.user32.EnumDisplayMonitors(0, 0, cbfunc, 0)
    return retval


def _monitorAreas():
    """Find the active and working area of each monitor.
    Source: code.activestate.com/recipes/460509-get-the-actual-and-usable-sizes-of-all-the-monitor
    """
    retval = []
    monitors = _getMonitors()
    for hMonitor, extents in monitors:
        data = [hMonitor]
        mi = MONITORINFO()
        mi.cbSize = ctypes.sizeof(MONITORINFO)
        mi.rcMonitor = RECT()
        mi.rcWork = RECT()
        ctypes.windll.user32.GetMonitorInfoA(hMonitor, ctypes.byref(mi))
        data.append(mi.rcMonitor.dump())
        data.append(mi.rcWork.dump())
        retval.append(data)
    return retval


def setCoordinatesToScreen(x, y, w, h, padding=0):
    """Using the position information of a window, find a location where it is not off screen.
    Use offset_low if the space at the right or top of the screen needs adjusting.
    Use offset_high if the space at the left or bottom of the screen needs adjusting.
    """
    monitor_adjusted = [(x1, y1, x2-w-padding, y2-h-padding) for x1, y1, x2, y2 in tuple(m[1] for m in _monitorAreas())]
    location_groups = zip(*monitor_adjusted)

    x_orig = x
    y_orig = y
    if monitor_adjusted:
        #Make sure window is within monitor bounds
        x_min = min(location_groups[0])
        x_max = max(location_groups[2])
        y_min = min(location_groups[1])
        y_max = max(location_groups[3])
        
        if x < x_min:
            x = x_min
        elif x > x_max:
            x = x_max
        if y < y_min:
            y = y_min
        elif y > y_max:
            y = y_max
        
        #Check offset to find closest monitor
        monitor_offsets = {}
        for monitor_location in monitor_adjusted:
            monitor_offsets[monitor_location] = 0
            x1, y1, x2, y2 = monitor_location
            if x < x1:
                monitor_offsets[monitor_location] += x1 - x
            elif x > x2:
                monitor_offsets[monitor_location] += x - x2
            if y < y1:
                monitor_offsets[monitor_location] += y1 - y
            elif y > y2:
                monitor_offsets[monitor_location] += y - y2

        #Check the window is correctly in the monitor
        x1, y1, x2, y2 = min(monitor_offsets.items(), key=lambda d: d[1])[0]
        if x < x1:
            x = x1
        elif x > x2:
            x = x2
        if y < y1:
            y = y1
        elif y > y2:
            y = y2

    #Reverse window padding if needed
    if x != x_orig:
        x -= padding
    if y != y_orig:
        y -= padding

    return (x, y)
