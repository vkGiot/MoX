# -*- coding: utf-8 -*-
"""
vkGiots MoX MusicMP3.ru Downloader
- usable via CLI and as Tkinter-based Window

@author         vkGiot <vkgiot@mail.ru>
@version        0.1.1-alpha
@license        MIT License
@website        https://github.com/vkGiot/MoX

@dependencies   FFmpeg   @ https://ffmpeg.org/
                         © Licensed under LGPLv2
                Requests @ http://docs.python-requests.org/en/master/
                         © Licensed under Apache 2.0

OWN AND USE AT YOUR OWN RISK
The use, distribution or possession of this program is may completely illegal 
in your country. You are responsible for your legal security, so either don't 
use it or don't get caught using it! This is just a fun project and I assume 
no warranty or legal rights!
"""

import sys
import tkinter as tk

from os import path
from threading import Thread
from mmp3 import MMP3, MMP3_URL


mox = None
class MoXDownloader():
    """Main MoX Tkinter Class
    
    @since  0.1.0
    @update 0.1.1
    """
    
    style = """
.top{
    padx: 10
    pady: 10
    background: #101418
}
.topline{
    height: 0
    relief: "flat"
    highlightthickness: 1
    highlightbackground: #303438
}
.topfield{
    width: 50
    relief: "flat"
    borderwidth: 5
    highlightthickness: 1
    background: #202428
    foreground: #ffffff
    insertbackground: #34bf49
    selectbackground: #34bf49
    highlightbackground: #505458
    highlightcolor: #34bf49
}
.topbutton{
    padx: 10
    pady: 7
    cursor: "hand2"
    relief: "flat"
    overrelief: "flat"
    borderwidth: 0
    foreground: #ffffff
    background: #34bf49
    highlightthickness: 0
    activeforeground: #ffffff
    activebackground: #202428
}
.main{
    padx: 10
    pady: 20
    background: #101418
}
.maincanvas{
    relief: "flat"
    background: #101418
    borderwidth: 0
    highlightthickness: 0
}
.maintracks{
    padx: 2
    background: #101418
}
.item{
    background: #101418
}
.itemline-v{
    height: 0
    relief: "flat"
    highlightthickness: 1
    highlightbackground: #101418
}
.itemline-h{
    width: 0
    relief: "flat"
    highlightthickness: 1
    highlightbackground: #101418
}
.itemnumber{
    width: 5
    foreground: #ffffff
    background: #34bf49
}
.itemtitle{
    anchor: "sw"
    padx: 10
    pady: 0
    foreground: #ffffff
    background: #303438
}
.itemalbum{
    anchor: "nw"
    padx: 10
    pady: 0
    foreground: #ffffff
    background: #303438
}
.itemstatus{
    width: 10
    foreground: #ffffff
    background: #303438
}
.itemaction{
    width: 10
    text: "R"
    foreground: #ffffff
    background: #303438
}
.bottom{
    padx: 10
    pady: 7
    background: #202428
}
.bottominner{
    background: #202428
}
.bottomline{
    height: 0
    relief: "flat"
    highlightthickness: 1
    highlightbackground: #404448
}
.statslinks{
    anchor: "w"
    foreground: #ffffff
    background: #202428
}
.statsaction{
    padx: 10
    pady: 10
    cursor: "hand2"
    relief: "flat"
    overrelief: "flat"
    compound: "right"
    borderwidth: 0
    foreground: #ffffff
    background: #34bf49
    activeforeground: #ffffff
    activebackground: #101418
    highlightthickness: 0
}
"""
    
    def parse(self, style):
        """Parse the LS (LiteStyles) Tkinter String
        
        @since  0.1.0
        """
        element = {}
        for line in style.splitlines():
            line = line.strip()
            
            if line == "" or len(line) <= 1:
                continue
            
            if line[0] == ".":
                line = line.replace(".", "")
                line = line.replace("{", "")
                element[line] = {}
                current = line
                continue
            
            if line == "}":
                current = None
            
            if current == None:
                continue
            
            parts = line.split(":")
            if len(parts) == 2:
                key = parts[0].strip().replace(":", "")
                value = parts[1].strip().replace("\"", "")
                value = value.replace("\'", "")
                element[current][key] = value
        return element
    
    def __init__(self):
        """Class Constructor
        
        @since  0.1.0
        @update 0.1.1
        """
        if type(self.style) is str:
            self.style = self.parse(self.style)
        
        # Init General
        self.urls = []
        self.tracks = {}
        self.finished = 0
        
        self.mmp3 = MMP3(None)
        self.inloop = False
        self.downloading = False
        
        # Get Module Path
        if getattr(sys, "frozen", False):
            self.path = path.dirname(path.realpath(sys.executable))
        else:
            self.path = path.dirname(path.realpath(__file__))
        
        # Init Tkinter
        self.root = tk.Tk()
        self.root.title("MoX - MusicMP3.ru Downloader")
        self.root.bind("<Return>", self.handle)
        self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        
        # Icon
        if sys.platform == "win32" or sys.platform == "win64":
            self.root.iconbitmap(path.join(self.path, "assets", "robot.ico"))
        elif sys.platform == "linux" or sys.platform == "linux2":
            pass # WTF...
        
        self.create()
    
    def create(self):
        """Create Main Tkinter Structure
        
        @since  0.1.0
        @update 0.1.1
        """
        self.valueField = tk.StringVar()
        self.valueButton = tk.StringVar()
        self.valueButton.set("Fetch Links")
        self.valueStats = tk.StringVar()
        self.valueStats.set("")
        self.valueAction = tk.StringVar()
        self.valueAction.set("Start Download")
        
        # Images
        self.iconPlay  = tk.PhotoImage(file=path.join(self.path, "assets", "play.gif"))
        self.iconPause = tk.PhotoImage(file=path.join(self.path, "assets", "pause.gif"))
        
        # Create Top
        self.top = tk.Frame(self.root, self.style["top"])
        self.top.grid(column=0, row=0)
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)
        
        self.topLine = tk.Frame(self.root, self.style["topline"])
        self.topLine.grid(column=0, row=1, sticky=("w", "e"))
        
        self.style["topfield"]["textvariable"] = self.valueField
        self.topField = tk.Entry(self.top, self.style["topfield"])
        self.topField.grid(column=0, row=0, padx=5, pady=5, sticky=("w", "e"))
        
        self.style["topbutton"]["command"] = self.handle
        self.style["topbutton"]["textvariable"] = self.valueButton
        self.topButton = tk.Button(self.top, self.style["topbutton"])
        self.topButton.grid(column=1, row=0, padx=5, pady=5, sticky=("w", "e"))
        self.topButton.bind("<Enter>", self.onmouse)
        self.topButton.bind("<Leave>", self.onmouse)
        
        # Create Main
        self.main = tk.Frame(self.root, self.style["main"])
        self.main.grid(column=0, row=2, sticky=("n", "e", "s", "w"))
        
        self.mainCanvas = tk.Canvas(self.main, self.style["maincanvas"])
        self.mainCanvas.pack(side="left", fill="both", expand=True)
        self.mainScroll = tk.Scrollbar(self.main, orient="vertical", command=self.mainCanvas.yview)
        self.mainScroll.pack(side="right", fill="y", expand=True)
        self.mainTracks = tk.Frame(self.mainCanvas, self.style["maintracks"])
        self.mainTracks.grid(column=0, row=0, sticky=("n", "e", "s", "w"))
        self.mainTracks.columnconfigure(0, weight=1)
        self.mainTracks.rowconfigure(0, weight=1)
        self.mainTracksID = self.mainCanvas.create_window((0, 0), window=self.mainTracks, anchor="nw")
        self.mainCanvas.configure(yscrollcommand=self.mainScroll.set)
        self.mainCanvas.bind("<Configure>", self.configure)
        self.mainCanvas.bind("<Enter>", lambda e: self.root.bind("<MouseWheel>", self.configure))
        self.mainCanvas.bind("<Leave>", lambda e: self.root.unbind("<MouseWheel>"))
        self.mainTracks.bind("<Configure>", self.configure)
        
        # Create Bottom
        self.bottom = tk.Frame(self.root, self.style["bottom"])
        self.bottom.grid(column=0, row=4, sticky=("n", "e", "s", "w"))
        self.bottom.columnconfigure(0, weight=1)
        self.bottom.rowconfigure(0, weight=1)
        self.bottomLine = tk.Frame(self.root, self.style["bottomline"])
        self.bottomLine.grid(column=0, row=3, sticky=("e", "w"))
        
        self.bottomInner = tk.Frame(self.bottom, self.style["bottominner"])
        self.bottomInner.grid(column=0, row=0, sticky=("n", "e", "s", "w"))
        self.bottomInner.columnconfigure(0, weight=1)
        self.bottomInner.rowconfigure(0, weight=1)
        
        self.style["statslinks"]["textvariable"] = self.valueStats
        self.statsLinks = tk.Label(self.bottomInner, self.style["statslinks"])
        self.statsLinks.grid(column=0, row=0, sticky=("e", "w"))
        
        self.style["statsaction"]["image"] = self.iconPlay
        self.style["statsaction"]["command"] = self.download
        self.style["statsaction"]["textvariable"] = self.valueAction
        self.statsAction = tk.Button(self.bottomInner, self.style["statsaction"])
        self.statsAction.grid(column=2, row=0, sticky=("e", "w"))
        self.statsAction.bind("<Enter>", self.onmouse)
        self.statsAction.bind("<Leave>", self.onmouse)
    
    def onmouse(self, event):
        """Awesome Button OnEnter/OnLeave Bind
        
        @since  0.1.1
        """
        if str(event.type) == "Enter" or str(event.type) == "7":
            if event.widget == self.statsAction and self.downloading is True:
                event.widget.configure(background="#cc3c3c")
            else:
                event.widget.configure(background="#248533")
        elif str(event.type) == "Leave" or str(event.type) == "8":
            if event.widget == self.statsAction and self.downloading is True:
                event.widget.configure(background="#ff4c4c")
            else:
                event.widget.configure(background="#34bf49")
    
    def configure(self, event):
        """Configure Scrollregion / Bind MouseWheel
        
        @since  0.1.0
        @update 0.1.1
        """
        if str(event.type) == "MouseWheel":
            self.mainCanvas.yview_scroll(int(-1*(event.delta/120)), "units")
            return True
        
        self.mainCanvas.itemconfig(self.mainTracksID, width=event.width)
        self.mainCanvas.configure(scrollregion=self.mainCanvas.bbox("all"))
        
    def link(self, num, track, status):
        """Create Track/Link Element
        
        @since  0.1.0
        @update 0.1.1
        """
        item = tk.Frame(self.mainTracks, self.style["item"])
        item.grid(column=0, row=num, columnspan=6, sticky=("n", "e", "s", "w"))
        item.columnconfigure(2, weight=1)
        
        # Line Handling
        itemLineT = tk.Frame(item, self.style["itemline-v"])
        itemLineL = tk.Frame(item, self.style["itemline-h"])
        itemLineR = tk.Frame(item, self.style["itemline-h"])
        itemLineB = tk.Frame(item, self.style["itemline-v"])
        itemLineT.grid(column=1, row=0, columnspan=3, sticky=("e", "w"))
        itemLineL.grid(column=0, row=1, rowspan=2, sticky=("n", "s"))
        itemLineR.grid(column=5, row=1, rowspan=2, sticky=("n", "s"))
        itemLineB.grid(column=1, row=3, columnspan=3, sticky=("e", "w"))
        
        # Item Content
        itemNumber = tk.Label(item, self.style["itemnumber"])
        itemTitle  = tk.Label(item, self.style["itemtitle"])
        itemAlbum  = tk.Label(item, self.style["itemalbum"])
        itemStatus = tk.Label(item, self.style["itemstatus"])
        itemNumber.grid(column=1, row=1, rowspan=2, sticky=("n", "e", "s", "w"))
        itemTitle .grid(column=2, row=1, sticky=("e", "w"), ipady=2)
        itemAlbum .grid(column=2, row=2, sticky=("e", "w"), ipady=2)
        itemStatus.grid(column=3, row=1, rowspan=2, sticky=("n", "e", "s", "w"))
        
        # Item Action
        #itemAction = tk.Label(item, self.style["itemaction"])
        #itemAction.bind("<Button-1>", lambda x: self.remove(x, item, track))
        #itemAction.grid(column=4, row=1, rowspan=2, sticky=("n", "e", "s", "w"))
        
        # Add Content
        itemNumber.configure(text=track["number"])
        itemTitle .configure(text=track["title"])
        itemAlbum .configure(text=track["artist"] + " - " + track["album"])
        itemStatus.configure(textvariable=status)
        return [item, itemNumber, itemTitle, itemAlbum, itemStatus];
        
    def handle(self, *args):
        """Handle 'Fetch Links' Action
        
        @since  0.1.0
        @update 0.1.1
        """
        url = self.valueField.get().strip()
        if len(url) <= 1:
            self.valueField.set("MoX needs a valid 'musicmp3.ru' URL! D:")
            return False
        
        # Test Field
        if url == "JoX":
            pending = tk.StringVar()
            pending.set("Pending")
            for i in range(0, 20):
                item = self.link(i, {
                    "title": "JoxJoX", "album": "JixJaxJux", "artist": "JoxJox", "number": str(i).zfill(2)
                }, pending)
            return True
        
        # Check URL
        url = MMP3_URL(url)
        if url is False:
            self.valueField.set("MoX supports 'musicmp3.ru' URLs only!")
            return False
        
        # Dupilicate URL
        if url in self.urls:
            self.valueField.set("MoX has already fetched this URL! :3")
            return False
        self.urls.append(url)
        
        # Fetch Tracks
        tracks = self.mmp3.fetch(url)
        if tracks == False:
            self.valueField.set("MoX wasn't able to fetch any track! :(")
            return False
        
        # Build Tracks
        for track in tracks:
            self.tracks[track["hash"]] = {
                "track": track,
                "status": tk.StringVar(),
                "elements": []
            }
            item = self.link(len(self.tracks), track, self.tracks[track["hash"]]["status"])
            self.tracks[track["hash"]]["status"].set("Pending")
            self.tracks[track["hash"]]["elements"] = item
        
        self.valueStats.set("%d / %d Downloads finished" % (self.finished, len(self.tracks)));
        self.valueField.set("")
        
        if self.finished == len(self.tracks) and self.downloading == True:
            self.download()
        return True
    
    def remove(self, event, item, track):
        """Removes an Single Track / Item
        
        @since  0.1.1
        """
        pass
    
    def download(self, *args):
        """Handle 'Start|Stop Download' Action
        
        @since  0.1.0
        @update 0.1.1
        """
        if self.downloading is False:
            if self.finished == len(self.tracks):
                return False
            
            if self.mmp3.start(self.response, True):
                self.downloading = True
                self.statsAction.configure(image=self.iconPause, background="#ff4c4c")
                self.style["statsaction"]["textvariable"].set("Stop Download")
        elif self.downloading is True:
            if self.mmp3.stop():
                self.downloading = False
                self.statsAction.configure(image=self.iconPlay, background="#34bf49")
                self.style["statsaction"]["textvariable"].set("Start Download")
    
    def response(self, track, status):
        """Response Callback for the MMP3 Class
        
        @since  0.1.0
        @update 0.1.1
        """
        if status[0] is True:
            if status[1] == 200:
                self.tracks[track["hash"]]["status"].set(status[2])
                self.tracks[track["hash"]]["elements"][4].configure(fg="#34bf49")
                
                self.finished += 1
                self.valueStats.set("%d / %d Downloads finished" % (self.finished, len(self.tracks)));
                
                if self.finished == len(self.tracks) and self.downloading == True:
                    self.download()
            else:
                split = str(status[2]).split(".")
                split = (split[0], "{:<02d}".format(int(split[1])))
                self.tracks[track["hash"]]["status"].set("%s.%s %%" % split)
                self.tracks[track["hash"]]["elements"][4].configure(fg="#ffffff")
        elif status[0] is False:
            self.tracks[track["hash"]]["status"].set("Error %d" % status[1])
            self.tracks[track["hash"]]["elements"][4].configure(fg="#ff4c4c")
        else:
            self.tracks[track["hash"]]["status"].set(status[1])
            self.tracks[track["hash"]]["elements"][4].configure(fg="#ffffff")
        return True
    
    def loop(self):
        """Tkinter MainLoop Function
        
        @since  0.1.0
        """
        self.inloop = True
        self.root.mainloop()
        return self.root
    
    def quit(self):
        """Tkinter quit/destroy Callback
        
        @since  0.1.0
        """
        self.mmp3.stop()
        self.root.destroy()
        self.root.quit()


class Process(Thread):
    """Main-Threading Tkinter Fix, which currently doesn't work as excpected :(
    
    @since  0.1.0
    """
    def __init__(self):
        """Process Contructor
        
        @since  0.1.0
        """
        Thread.__init__(self)


def main():
    """Main Instance Function
    
    @since  0.1.0
    """
    mox = MoXDownloader()
    SecondThread = Process()
    mox.root.after(50, SecondThread.start)
    mox.loop()


if __name__ == "__main__":
    main()
