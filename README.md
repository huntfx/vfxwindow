# VFXWindow
Qt Window class for designing tools to be compatible between multiple VFX programs.

The main purpose of the class is to integrate into the program UI, but it also contains helpful features such as safely dealing with callbacks and automatically saving the window position.

The intended usage is to make your window class inherit `VFXWindow` - which is an instance of `QMainWindow`. By calling `cls.show()`, it will launch the correct window type based on what program is loaded, and what settings were previously saved.

This is perfectly stable, but there is still plenty that needs improvement. Maya, Nuke, 3DS Max, Houdini, Blender, Substance Designer, Unreal and Fusion are currently supported, though any help to extend those would be appreciated, as well as support for any other applications.

### Installation
    pip install vfxwindow

### Basic Example:
```python
class MyWindow(VFXWindow):
    WindowID = 'unique_window_id'
    WindowName = 'My Window'

    def __init__(self, parent=None, **kwargs):
        super(MyWindow, self).__init__(parent, **kwargs)
        # Setup window here

        # Setup callbacks, but wait until the program is ready
        self.deferred(self.newScene)

    def newScene(self, *args):
        """Example: Delete and reapply callbacks after loading a new scene."""
        self.removeCallbacks('sceneNewCallbacks')
        if self.maya:
            self.addCallbackScene('kAfterNew', self.newScene, group='sceneNewCallbacks')
        elif self.nuke:
            self.addCallbackOnCreate(self.newScene, nodeClass='Root', group='sceneNewCallbacks')

if __name__ == '__main__':
    MyWindow.show()
```

### Support / Compatibility
✔️ Working  /  ❔ Untested  /  ❌ Not Working
|                    | Standard Window | Docked Window | Callbacks | Tested Versions | [Linux](# "Tested in Linux Mint.")  | Windows | MacOs |
| ------------------ | -------- | -------- | -------- | -------- | -------- | --------- | ------- |
| Maya               | ✔️ | [✔️](# "Uses `workspaceControl` or falls back to `dockControl` for pre Maya 2017, saves/restores location of window.") | ✔️ | [2011-2016](# "Docked windows use `dockControl`, tested lightly on 2016."), [2017+](# "Docked windows use `workspaceControl`.") | ✔️ | ✔️ | ❔ |
| Maya (Standalone)  | ✔️ | | ✔️ | | ❔ | ✔️ | ❔ |
| Nuke               | ✔️ | [✔️](# "Uses `registerWidgetAsPanel` to dock window in a panel, saves/restores location of panel only when docked (not floating).") | ✔️ | 9-12 | ❔ | ✔️ | ❔ |
| Nuke (Terminal)    | ✔️ | | ✔️ | | ❔ | ✔️ | ❔ |
| Houdini            | ✔️ | ❌ | ❌ | 16-19 | ✔️ | ✔️ | ❔ |
| Unreal Engine      | ✔️ | ❌ | ❌ | 4.19-4.23, 5.0-5.3 | [❌](# "Tested on UE5.") | ✔️ | ❔ |
| Blender            | ✔️ | ❌ | ✔️ | 2.8-3.4 | ❔ | ✔️ | ❔ |
| 3ds Max            | ✔️ | ❌ | ❌ | 2018-2020 | ❔ | [✔️](# "Tested previously but unable to confirm.") | ❔ |
| Substance Painter  | ✔️ | [✔️](# "Uses `substance_painter.ui.add_dock_widget`, does not save/restore location of window.") | ❌ | 8.3 | ✔️ | ✔️ | ❔ |
| Substance Designer | ✔️ | [✔️](# "Uses `sd.getContext().getSDApplication().getQtForPythonUIMgr().newDockWidget`, does not save/restore location of window.") | ❌ | 2019.3, 7.1, 12.3 | ✔️ | ✔️ | ❔ |
| Blackmagic Fusion  | ✔️ | ❌ | ❌ | 9 | ❔ | [✔️](# "Unable to read Fusion version, and causes recursion error if calling `show`/`hide`/`setVisible`.") | ❔ |
| CryEngine Sandbox  | ✔️ | [❌](# "There's a `SandboxBridge.register_window` function, but I was not able to figure it out.") | ❌ | 5.7 | ❔ | [✔️](# "Causes recursion error if calling `show`/`hide`/`setVisible`.") | ❔ |
| Standalone Python  | ✔️ | | | 2.7 (Qt4), 3.7-3.9 (Qt5) | ❔ | ✔️ | ❔ |

### Features
 - Automatically save/restore window position
 - Move window to screen if out of bounds (windows only)
 - Keep track of callbacks to remove groups if required, and clean up on window close
 - Keep track of signals to remove groups if required
 - Display a popup message that forces control
 - Set palette to that of another program
 - Auto close if opening a duplicate window
 - Close down all windows at once
 - Create dialog windows automatically attached to the application (and return data)

### Running with Non-Python Applications
Certain Windows applications have dispatch based COM interface, which will allow a link between Python and the application. See [photoshop-scripting-python](https://github.com/lohriialo/photoshop-scripting-python) for an example on how to connect to an application.

Currently there is no way of launching `VFXWindow` from inside these applications.

### Special Thanks
 - [Blue Zoo](https://www.blue-zoo.co.uk/) - I've been building this up while working there
 - [Lior Ben Horin](https://gist.github.com/liorbenhorin): [Simple_MayaDockingClass.py](https://gist.github.com/liorbenhorin/69da10ec6f22c6d7b92deefdb4a4f475) - used for main Maya docking code
 - [Fredrik Averpil](https://github.com/fredrikaverpil): [pyvfx-boilerplate](https://github.com/fredrikaverpil/pyvfx-boilerplate) - helped with palettes, Nuke, and pre-2017 Maya
