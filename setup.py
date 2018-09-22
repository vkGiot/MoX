# -*- coding: utf-8 -*-
import os, sys, cx_Freeze

os.environ["TK_LIBRARY"]  = os.path.join(sys.exec_prefix, "tcl", "tk8.6")
os.environ["TCL_LIBRARY"] = os.path.join(sys.exec_prefix, "tcl", "tcl8.6")

base = None
if sys.platform == "win32":
    base = "Win32GUI"

cx_Freeze.setup(
    name = "MoX",
    author = "vkGiot",
    version = "0.1.1",
    description = "A Downloader-Script for MusicMP3.ru",
    options = {"build_exe": {
        "packages": ["tkinter", "requests"],
        "include_files": [
            "ffmpeg/", "assets/", 
            os.path.join(sys.exec_prefix, "DLLs", "tk86t.dll"),
            os.path.join(sys.exec_prefix, "DLLs", "tcl86t.dll")
        ]
    }},
    executables = [cx_Freeze.Executable("mox.py", base=base), cx_Freeze.Executable("mmp3.py")]
)