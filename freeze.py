import cx_Freeze as c

# REMEMBER !! THE SHELL LINE IS :
# py freeze.py build_exe

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["tkinter", "os", "ctypes", "mne", "pathlib", "psutil", "datetime",
                                  "threading", "numpy", "scipy", "matplotlib", "mne_qt_browser", "qtpy", "PyQt6"]}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = "Win32GUI"

c.setup(name = "MNE Explorer",
        version = "0.1",
        description = "MNE Explorer 1.0",
        options = {"build_exe": build_exe_options},
        executables = [c.Executable("mne_explorer.py", base=base)])