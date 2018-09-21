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
import os, sys, time, subprocess, argparse
import multiprocessing.dummy as multiprocessing
import requests
from html.parser import HTMLParser

##
##  MusicMP3 URL CHECK
##
def MMP3_URL(url):
    if type(url) != str:
        return False
    
    ## Format URL
    if url.startswith("http:"):
        url = url.replace("http:", "https:", 1)
    elif not url.startswith("https:"):
        url = "https://" + url
    if url.startswith("https://www."):
        url = url.replace("https://www.", "https://")
        
    # Check URL
    if not url.startswith("https://musicmp3.ru"):
        return False
    
    ## Success
    return url

##
##  MusicMP3 HTML PARSER
##
class MMP3_Parser(HTMLParser):
    def __init__(self):
        self.data = {
            "album": "Unknown",
            "artist": "Unkown",
            "release": None,
            "tracks": []
        }
        self.track = None
        self.listen = False
        super().__init__()
    
    # Sanitize Text
    def sanitize(self, data):
        data = data.replace(": ", " - ")
        data = data.replace(":", "")
        data = data.replace("\\", "")
        data = data.replace("/", "")
        data = data.replace("*", "")
        data = data.replace("?", "")
        data = data.replace("\"", "")
        data = data.replace("<", "")
        data = data.replace(">", "")
        data = data.replace("|", "")
        return data.strip()
    
    # Starting HTML Tag
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs);
        
        if tag == "a":
            if "class" in attrs and attrs["class"] == "player__play_btn js_play_btn":
                self.track = len(self.data["tracks"])
                self.data["tracks"].append({
                    "hash": attrs["rel"],
                    "title": "",
                    "number": str(self.track+1).zfill(2),
                    "filename": str(self.track+1).zfill(2) + " - "
                })
                
        if tag == "td":
            if "class" in attrs and attrs["class"] == "song__name":
                self.listen = "song"
        
        if tag == "h1":
            if "class" in attrs and attrs["class"] == "page_title__h1":
                self.listen = "album"
        
        if tag == "span":
            if "itemprop" in attrs and attrs["itemprop"] == "byArtist":
                self.listen = "artist"
            elif "itemprop" in attrs and attrs["itemprop"] == "dateCreated":
                self.listen = "release"
    
    # Endign HTML Tag
    def handle_data(self, data):
        if self.listen == "album":
            self.data[self.listen] = self.sanitize(data)
            
        if self.listen == "artist":
           self.data[self.listen] = self.sanitize(data)
            
        if self.listen == "release":
           self.data[self.listen] = "(" + self.sanitize(data) + ")"
            
        if self.listen == "song" and self.track != None:
            self.data["tracks"][self.track]["title"] = self.sanitize(data)
            self.data["tracks"][self.track]["filename"] += self.sanitize(data)
        
        self.track = None
        self.listen = False

##
##  MusicMP3 DOWNLOADER SCRIPT
##
class MMP3:
    headers = {
        "Host": "musicmp3.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:42.0) Gecko/20100101 Firefox/42.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU;q=0.7,ru;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    listener = "https://listen.musicmp3.ru/"
    
    # Constructor
    def __init__(self, path):
        self.path = path
        self.pool = None
        self.running = False
        self.callback = self.call
        
        self.current = {}       # Current Downloads
        self.finished = {}      # Finished Downloads
        self.downloads = {}     # All Downloads
        
        self.processes = {}     # Current Proccesses
        
    # Fetch URL
    def fetch(self, url):
        response = requests.get(url, headers=self.headers);
        if response.status_code != 200:
            return False
        
        parser = MMP3_Parser()
        parser.feed(response.text)
        if len(parser.data["tracks"]) == 0:
            return False
        
        new = []
        for track in parser.data["tracks"]:
            self.downloads[track["hash"]] = track
            self.downloads[track["hash"]]["album"] = parser.data["album"]
            self.downloads[track["hash"]]["artist"] = parser.data["artist"]
            self.downloads[track["hash"]]["release"] = parser.data["release"]
            new.append(self.downloads[track["hash"]])
        return new
    
    # Download Track
    def download(self, track):
        headers = self.headers;
        
        # Get Data
        content = requests.get("https://listen.musicmp3.ru/" + track["hash"], headers=headers, stream=True)
        if content.status_code != 200:
            self.callback(track, "Error: " + str(content.status_code))
            time.sleep(1.5)
            
            self.callback(track, "Reload")
            time.sleep(0.25)
            return self.download(track)
        
        # Prepare Folder
        dirname = track["artist"] + " - " + track["album"];
        if track["release"] is not None:
            dirname += " " + track["release"]
            
        path = os.path.join(self.path, track["artist"], dirname)
        if not os.path.isdir(path):
            os.makedirs(path)
        
        file = os.path.join(path, track["filename"])
        
        # Load Data
        size = 0
        with open(file + ".mpeg", "wb") as f:
            for chunk in content.iter_content(chunk_size=1024):
                if self.running is not True:
                    f.close()
                    os.remove(file + ".mpeg")
                    break;
                if chunk:
                    f.write(chunk)
                    size = size+1024
                    self.callback(track, str(round(size*100 / int(content.headers["content-length"]), 2)) + "%")
        
        if self.running is False and os.path.isfile(file + ".mpeg") is False:
            self.callback(track, "Abort")
            return False
            
        # Convert Data
        self.callback(track, "Converting...")
        if subprocess.getstatusoutput("ffmpeg -h")[0] == 0:
            test = subprocess.check_call(["ffmpeg", "-i", file + ".mpeg", file + ".mp3"]);
            if test == 0:
                self.callback(track, "Finished")
                os.remove(file + ".mpeg")
        elif os.name == 'nt':
            if getattr(sys, "frozen", False):
                path = os.path.dirname(os.path.realpath(sys.executable))
            else:
                path = os.path.dirname(os.path.realpath(__file__))
            test = subprocess.check_call([os.path.join(path, "ffmpeg", "ffmpeg"), "-i", file + ".mpeg", file + ".mp3"]);
            if test == 0:
                self.callback(track, "Finished")
                os.remove(file + ".mpeg")
        else:
            self.callback(track, "FFMPEG missing")
        
        name = multiprocessing.current_process().name
        self.finished[track["hash"]] = self.current[name]
        del self.current[name]
        return self.handle()
    
    ## Handle Downloader-Proccess
    def handle(self):
        name = multiprocessing.current_process().name
        
        if name not in self.processes:
            self.processes[name] = multiprocessing.current_process()
        
        ticket = next(iter(self.downloads))
        self.current[name] = self.downloads[ticket]
        del self.downloads[ticket];
        return self.download(self.current[name])
    
    # Callable Fallback
    def call(self, *args):
        pass
    
    # Start Downloader
    def start(self, callback, pool):
        if callable(callback):
            self.callback = callback
        else:
            self.callback = self.call
        
        self.running = True
        if pool is False:
            self.pool = False
            return self.handle()
        
        self.pool = multiprocessing.Pool(2)
        for i in range(0, self.pool._processes):
            self.pool.apply_async(self.handle)
        return True
    
    # Stop Downloader
    def stop(self):
        if self.running is not True:
            return True
        
        for track in self.current:
            track = self.current[track];
            self.downloads[track["hash"]] = track
        
        self.pool.terminate()
        self.curent = {}
        self.running = False
        return True

##
##  MMP3 __main__ CLI Call
##
def main():
    parser = argparse.ArgumentParser(
           description="Download tracks from MusicMP3.ru"
    )
    parser.add_argument("URL", 
           help="The MusicMP3.ru URL"
    )
    parser.add_argument("-p", "--path", 
           help="The download path for the Tracks"
    )
    parser.add_argument("-f", "--fetchonly",
           help="Just get the respective download links",
           action='store_true'
    )
    
    con = parser.parse_args();
    con.URL = MMP3_URL(con.URL);
    if con.URL is False:
        parser.error("The passed MusicMP3.ru URL is invalid!")
    
    if con.path is None:
        if getattr(sys, "frozen", False):
            con.path = os.path.dirname(os.path.realpath(sys.executable))
        else:
            con.path = os.path.dirname(os.path.realpath(__file__))
    
    if os.path.isdir(con.path) is False:
        parser.error("The Download Path doesn't exist os isn't writable!")
    
    mmp3 = MMP3(con.path)
    tracks = mmp3.fetch(con.URL)
    
    if tracks == False or len(tracks) == 0:
        parser.error("The passed MusicMP3.ru URL seems invalid or doesn't contain any valid Track!")
    
    if con.fetchonly is True:
        for track in tracks:
            print("https://listen.musicmp3.ru/" + track["hash"])
        parser.exit(200, "Links have been successfully fetched!")
    
    for track in tracks:
        mmp3.running = True
        mmp3.start(progress, False)
        
# CLI ProgressBar
def progress(track, string):
    if string.endswith("%"):
        num = string.split(".")[0]
        title = track["album"] + " - " + track["title"]
        
        sys.stdout.write("\r%s - %d%%" % (title,int(num)))
        sys.stdout.flush()
        return True
    
    sys.stdout.write("\r%s%%" % string)
    sys.stdout.flush()
    return True;

if __name__ == "__main__":
    main()
