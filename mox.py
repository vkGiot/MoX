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
import os, time, threading
from tkinter import *
from mmp3 import MMP3

##
## TKINTER INTERFACE
##
mox = None
class MoXDownloader():
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
    highlightbackground: "#303438"
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
    padx: 5
    pady: 5
    cursor: "hand2"
    relief: "flat"
    overrelief: "flat"
    borderwidth: 0
    foreground: #ffffff
    background: #34bf49
    highlightbackground: #101418
    highlightcolor: #101418
    highlightthickness: 1
    activebackground: #70d27f
    activeforeground: #ffffff
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
.bottom{
    padx: 10
    pady: 10
    background: #34bf49
}
.bottomline{
    height: 0
    relief: "flat"
    highlightthickness: 1
    highlightbackground: #000000
}
.statslinks{
    anchor: "w"
    foreground: #ffffff
    background: #34bf49
}
.statswrapper{
    padx: 1
    pady: 1
    background: #101418
}
.statsaction{
    padx: 5
    pady: 5
    cursor: "hand2"
    relief: "flat"
    overrelief: "flat"
    borderwidth: 0
    foreground: #ffffff
    background: #101418
    activeforeground: #ffffff
    activebackground: #34bf49
    highlightthickness: 0
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
"""
    
    # Parse Style
    def parse(self, style):
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
    
    # Constructor
    def __init__(self):
        if type(self.style) is str:
            self.style = self.parse(self.style)
        
        # Get Downloads Folder
        if "APPDATA" in os.environ:
            downloads = os.path.abspath(os.getenv("APPDATA") + r"..\\..\\..\\")
        else:
            downloads = os.path.expanduser("~")
        if os.path.isdir(os.path.join(downloads, "Music")):
            downloads = os.path.join(downloads, "Music")
        elif os.path.isdir(os.path.join(downloads, "Downloads")):
            downloads = os.path.join(downloads, "Downloads")
        
        # Init General
        self.pool = None
        self.urls = []
        self.mmp3 = MMP3(downloads)
        self.items = {}
        self.inloop = False
        
        # Init Tkinter
        self.root = Tk()
        self.root.title("MoX - MusicMP3.ru Downloader")
        self.root.bind("<Return>", self.handle)
        self.root.resizable(0,0)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        self.create()
    
    # Create Window
    def create(self):
        self.valueField = StringVar()
        self.valueButton = StringVar()
        self.valueButton.set("Fetch Links")
        self.valueStats = StringVar()
        self.valueStats.set("")
        self.valueAction = StringVar()
        self.valueAction.set("Start Download")
        
        # Create Top
        self.top = Frame(self.root, self.style["top"])
        self.top.grid(column=0, row=0)
        self.top.columnconfigure(0, weight=1)
        self.top.rowconfigure(0, weight=1)
        
        self.topLine = Frame(self.root, self.style["topline"])
        self.topLine.grid(column=0, row=1, sticky=(W, E))
        
        self.style["topfield"]["textvariable"] = self.valueField
        self.topField = Entry(self.top, self.style["topfield"])
        self.topField.grid(column=0, row=0, padx=5, pady=5, sticky=(W, E))
        
        self.style["topbutton"]["command"] = self.handle
        self.style["topbutton"]["textvariable"] = self.valueButton
        self.topButton = Button(self.top, self.style["topbutton"])
        self.topButton.grid(column=1, row=0, padx=5, pady=5, sticky=(W, E))
        
        # Create Main
        self.main = Frame(self.root, self.style["main"])
        self.main.grid(column=0, row=2, sticky=(N, W, E, S))
        
        self.mainCanvas = Canvas(self.main, self.style["maincanvas"])
        self.mainCanvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.mainScroll = Scrollbar(self.main, orient=VERTICAL, command=self.mainCanvas.yview)
        self.mainScroll.pack(side=RIGHT, fill=Y, expand=True)
        self.mainTracks = Frame(self.mainCanvas, self.style["maintracks"])
        self.mainTracks.grid(column=0, row=0, sticky=(N, E, S, W))
        self.mainTracks.columnconfigure(0, weight=1)
        self.mainTracks.rowconfigure(0, weight=1)
        self.mainTracksID = self.mainCanvas.create_window((0, 0), window=self.mainTracks, anchor="nw")
        self.mainCanvas.configure(yscrollcommand=self.mainScroll.set)
        self.mainCanvas.bind("<Configure>", self.configure)
        self.mainTracks.bind("<Configure>", self.configure)
        
        # Create Bottom
        self.bottom = Frame(self.root, self.style["bottom"])
        self.bottom.grid(column=0, row=4, sticky=(N, W, E, S))
        self.bottom.columnconfigure(0, weight=1)
        self.bottom.rowconfigure(0, weight=1)
        self.bottomLine = Frame(self.root, self.style["bottomline"])
        self.bottomLine.grid(column=0, row=3, sticky=(W, E))
        
        self.style["statslinks"]["textvariable"] = self.valueStats
        self.statsLinks = Label(self.bottom, self.style["statslinks"])
        self.statsLinks.grid(column=0, row=0, sticky=(W, E))
        
        self.statsWrapper = Frame(self.bottom, self.style["statswrapper"])
        self.statsWrapper.grid(column=1, row=0, sticky=(W, E))
        
        self.style["statsaction"]["command"] = self.download
        self.style["statsaction"]["textvariable"] = self.valueAction
        self.statsAction = Button(self.statsWrapper, self.style["statsaction"])
        self.statsAction.grid(column=1, row=0, sticky=(W, E))
        
    # Configure Scrollregion
    def configure(self, event):
        self.mainCanvas.itemconfig(self.mainTracksID, width=event.width)
        self.mainCanvas.configure(scrollregion=self.mainCanvas.bbox("all"))
        
    # Create Link
    def link(self, number, title, album, status, num):
        item = Frame(self.mainTracks, self.style["item"])
        item.grid(column=0, row=num, columnspan=5, sticky=(N, E, S, W))
        item.columnconfigure(2, weight=1)
        
        # Line Handling
        itemLineT = Frame(item, self.style["itemline-v"])
        itemLineL = Frame(item, self.style["itemline-h"])
        itemLineR = Frame(item, self.style["itemline-h"])
        itemLineB = Frame(item, self.style["itemline-v"])
        itemLineT.grid(column=1, row=0, columnspan=3, sticky=(W, E))
        itemLineL.grid(column=0, row=1, rowspan=2, sticky=(N, S))
        itemLineR.grid(column=4, row=1, rowspan=2, sticky=(N, S))
        itemLineB.grid(column=1, row=3, columnspan=3, sticky=(W, E))
        
        # Item Content
        itemNumber = Label(item, self.style["itemnumber"])
        itemTitle  = Label(item, self.style["itemtitle"])
        itemAlbum  = Label(item, self.style["itemalbum"])
        itemStatus = Label(item, self.style["itemstatus"])
        itemNumber.grid(column=1, row=1, rowspan=2, sticky=(N, E, S, W))
        itemTitle .grid(column=2, row=1, sticky=(W, E), ipady=2)
        itemAlbum .grid(column=2, row=2, sticky=(W, E), ipady=2)
        itemStatus.grid(column=3, row=1, rowspan=2, sticky=(N, E, S))
        
        # Add Content
        itemNumber.configure(text=number)
        itemTitle .configure(text=title)
        itemAlbum .configure(text=album)
        itemStatus.configure(textvariable=status)
        return [item, itemNumber, itemTitle, itemAlbum, itemStatus];
        
    # Handle URL Field
    def handle(self, *args):
        url = self.valueField.get().strip()
        
        ## Empty Field
        if len(url) <= 1:
            self.valueField.set("MoX needs a valid 'musicmp3.ru' link! D:")
            return False
        
        ## Test Field
        if url == "JoX":
            pending = StringVar()
            pending.set("Pending")
            for i in range(0, 20):
                item = self.link(str(i+1), "JoxJox", "Joxen Musicans", pending, i)
            return True
        
        ## Format URL
        if url.startswith("http:"):
            url = url.replace("http:", "https:", 1)
        elif not url.startswith("https:"):
            url = "https://" + url
        if url.startswith("https://www."):
            url = url.replace("https://www.", "https://")
        
        # Check URL
        if not url.startswith("https://musicmp3.ru"):
            self.valueField.set("MoX supports links from 'musicmp3.ru' only!")
            return False
        
        # Dupilicate URL
        if url in self.urls:
            self.valueField.set("MoX has already fetched this link! :3")
            return False
        
        # Fetch Tracks
        tracks = self.mmp3.fetch(url)
        if tracks == False:
            self.valueField.set("MoX wasn't able to fetch any track! :(")
            return False
        
        # Build Tracks
        for track in tracks:
            self.items[track["hash"]] = {
                "track": track,
                "status": StringVar(),
                "elements": []
            }
            item = self.link(track["number"], track["title"], track["album"], self.items[track["hash"]]["status"], len(self.items))
            
            self.items[track["hash"]]["status"].set("Pending")
            self.items[track["hash"]]["elements"] = item
        
        self.valueField.set("")
        return True
    
    # Handle Download Button
    def download(self, *args):
        if self.style["statsaction"]["textvariable"].get() == "Stop Download":
            if self.mmp3.stop():
                self.style["statsaction"]["textvariable"].set("Start Download")
        else:
            if self.mmp3.start(self.response, True):
                self.style["statsaction"]["textvariable"].set("Stop Download")
    
    # Handle MMP3 response
    def response(self, track, status):
        self.items[track["hash"]]["status"].set(status)
        
        if status == "Finished":
            self.items[track["hash"]]["elements"][4].configure(fg="#34bf49")
        elif status.startswith("Error"):
            self.items[track["hash"]]["elements"][4].configure(fg="#ee0000")
        else:
            self.items[track["hash"]]["elements"][4].configure(fg="#ffffff")
        return True
    
    # Start Mainloop
    def loop(self):
        self.inloop = True
        self.root.mainloop()
        return self.root
    
    # Quit JoX Downloader
    def quit(self):
        self.mmp3.stop()
        self.root.destroy()
        self.root.quit()

##
##  THREADING / TKINTER FIX
##
class Process(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

##
##  MAIN FUNCTION
##
def main():
    mox = MoXDownloader()
    SecondThread = Process()
    mox.root.after(50, SecondThread.start)
    mox.loop()

if __name__ == "__main__":
    main()
