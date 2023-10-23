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

### Compatibility
✔️ Working  /  ❔ Untested  /  ❌ Not Working
|                    | Linux | Windows | MacOs |
| ------------------ | -------- | --------- | ------- |
| Maya               | ✔️<sup>1</sup> | ✔️ | ❔ |
| Maya Standalone    | ❔ | ✔️ | ❔ |
| Houdini            | ✔️<sup>1</sup> | ✔️ | ❔ |
| Unreal Engine      | ❌<sup>1</sup> | ✔️ | ❔ |
| Blender            | ❔ | ✔️ | ❔ |
| Nuke               | ❔ | ✔️ | ❔ |
| Nuke Terminal      | ❔ | ✔️ | ❔ |
| 3ds Max            | ❔ | ✔️<sup>2</sup> | ❔ |
| Substance Painter  | ✔️<sup>1</sup> | ✔️ | ❔ |
| Substance Designer | ✔️<sup>1</sup> | ✔️ | ❔ |
| Blackmagic Fusion  | ❔ | ✔️<sup>2</sup> | ❔ |
| Python             | ❔ | ✔️ | ❔ |

<sup>1</sup> Tested in Linux Mint.<br/>
<sup>2</sup> Unable to get version, and causes recursion error if calling `show`/`hide`/`setVisible`.<br/>

 - Maya:
    - 2011-2016, tested lightly on 2016, standard, docked (`pymel.core.dockControl`), standalone, callbacks
    - 2017+, tested on 2017-2019-2022-2023 - standard, docked (`pymel.core.workspaceControl`), standalone, callbacks
 - Nuke:
    - 9.0-12.0
    - standard window, docked (`nukescripts.panels`), callbacks
 - Substance Designer:
    - tested on 2019.3 (Windows), 7.1 (Linux)
    - standard window, docked (unable to save/load position)
 - 3D Studio Max:
    - 2018+, 2020
    - standard window
 - Houdini:
    - 16.0, 19.5
    - standard window
 - Blender:
    - 2.8, 3.1
    - standard window, callbacks
 - Unreal Engine:
    - 4.19+, 4.23, 5.0, 5.3
    - standard window
 - Fusion:
    - tested on 9.0
    - standard window
 - Standalone:
    - Qt4, Qt5
    - 2.7, 3.4+, 3.7, 3.9
    - standard window

### Generic Features
 - Automatically save/restore window position
 - Move window to screen if out of bounds (windows only)
 - Keep track of callbacks to remove groups if required, and clean up on window close
 - Keep track of signals to remove groups if required
 - Display a popup message that forces control
 - Set palette to that of another program
 - Auto close if opening a duplicate window
 - Close down all windows at once
 - Create dialog windows automatically attached to the application (and return data)

### Maya Features
 - Dock window using workspaceControl
 - Save/restore position of workspaceControl window (floating+docked)
 - Easy access to callbacks

### Nuke Features
 - Dock window as a panel
 - Save/restore location of panel (docked only)
 - Easy access to callbacks

### Blender Features
 - Easy access to callbacks

### Substance Features
 - Dock window into panels

### Non-Python Applications
Certain Windows applications have dispatch based COM interface, which will allow a link between Python and the application. See [photoshop-scripting-python](https://github.com/lohriialo/photoshop-scripting-python) for an example on how to connect to an application.

Currently there is no way of launching `VFXWindow` from inside these applications.

### Special Thanks
 - [Blue Zoo](https://www.blue-zoo.co.uk/) - I've been building this up while working there
 - [Lior Ben Horin](https://gist.github.com/liorbenhorin): [Simple_MayaDockingClass.py](https://gist.github.com/liorbenhorin/69da10ec6f22c6d7b92deefdb4a4f475) - used for main Maya docking code
 - [Fredrik Averpil](https://github.com/fredrikaverpil): [pyvfx-boilerplate](https://github.com/fredrikaverpil/pyvfx-boilerplate) - helped with palettes, Nuke, and pre-2017 Maya
