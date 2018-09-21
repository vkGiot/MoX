# -*- coding: utf-8 -*-
"""
vkGiots MoX MusicMP3.ru Downloader
- usable via CLI and as Tkinter-based Window

@author         vkGiot <vkgiot@mail.ru>
@version        0.1.0-alpha
@license        MIT License
@website        https://github.com/vkGiot/MoX

@dependencies   FFmpeg   @ https://ffmpeg.org/
                         © Licensed under LGPLv2
                Requests @ http://docs.python-requests.org/en/master/
                         © Licensed under Apache 2.0

OWN AND USE AT YOUR DOWN RISK
The use, distribution or possession of this program is may completely illegal 
in your country. So make sure its legal in your country, or nobody sees you!
I just wrote this program for fun, and assume no warranty or legal rights.
"""

import mox, mmp3

__all__ = ["mox", "mmp3"]
__version__ = "0.1.0"
__status__ = "Alpha"

if __name__ == "__main__":
    mox.main()