# -*- coding: utf-8 -*-
"""
vkGiots MoX MusicMP3.ru Downloader
- usable via CLI and as Tkinter-based Window

@author         vkGiot <vkgiot@mail.ru>
@version        0.1.2-alpha
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

import os
import sys
import time
import subprocess
import argparse
import requests

from multiprocessing import current_process
from multiprocessing.dummy import Pool

from html.parser import HTMLParser


def MMP3_URL(url):
    """Sanitize and Check the MusicMP3.ru URL

    @since  0.1.0
    """
    if type(url) != str:
        return False

    # Format URL
    if url.startswith("http:"):
        url = url.replace("http:", "https:", 1)
    elif not url.startswith("https:"):
        url = "https://" + url
    if url.startswith("https://www."):
        url = url.replace("https://www.", "https://")

    # Check URL
    if not url.startswith("https://musicmp3.ru"):
        return False
    return url


class MMP3_Parser(HTMLParser):
    """HTML Parser for the MusicMP3.ru Page Content

    @since  0.1.0
    """

    def __init__(self):
        """MMP3 HTML Parser Constructor

        @since  0.1.0
        """
        self.data = {
            "album": "Unknown",
            "artist": "Unkown",
            "release": None,
            "tracks": []
        }
        self.track = None
        self.listen = False
        self.classname = "player__play_btn js_play_btn"
        super().__init__()

    def sanitize(self, data):
        """Sanitize Text Content (I'm not quite sure about Python's RegExp yet)

        @since  0.1.0
        """
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

    def handle_starttag(self, tag, attrs):
        """Handle HTML Start Tags

        @since  0.1.0
        """
        attrs = dict(attrs)

        if tag == "a":
            if "class" in attrs and attrs["class"] == self.classname:
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

    def handle_data(self, data):
        """Handle HTML Inner Content

        @since  0.1.0
        @update 0.1.2
        """
        if self.listen in ["album", "artist", "release"]:
            self.data[self.listen] = self.sanitize(data)

        if self.listen == "song" and self.track is not None:
            self.data["tracks"][self.track]["title"] = self.sanitize(data)
            self.data["tracks"][self.track]["filename"] += self.sanitize(data)

        self.track = None
        self.listen = False


class MMP3:
    """Main MMP3 Class, where the Magix happens

    @since  0.1.0
    """
    h = {
        "Host": "musicmp3.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:42.0) Gecko/20100101 Firefox/42.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU;q=0.7,ru;q=0.3",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    li = "https://listen.musicmp3.ru/"

    def __init__(self, config={}):
        """MMP3 Constructor

        @since  0.1.0
        @update 0.1.2
        """
        path = None

        # Validate Download Path
        if "path" in config:
            path = config["path"]
            del config["path"]
        if path is None or os.path.isdir(path) is False:
            if "APPDATA" in os.environ:
                path = os.path.abspath(os.getenv("APPDATA") + r"..\\..\\..\\")
            else:
                path = os.path.expanduser("~")
            if os.path.isdir(os.path.join(path, "Music")):
                path = os.path.join(path, "Music")
            elif os.path.isdir(os.path.join(path, "Downloads")):
                path = os.path.join(path, "Downloads")

        # Validate Configuration
        self.c = {
            "path": path,
            "dirname": "%artist%/%artist% - %album% (%release%)",
            "filename": "%number% - %title%"
        }
        for c in config:
            if c in self.c and type(config[c]) == str:
                self.c[c] = config[c].strip()

        # Set Class Variables
        self.path = path
        self.pool = None
        self.running = False
        self.callback = self._cb_status

        self.tickets = []       # Download Tickets
        self.current = {}       # Current Downloads
        self.finished = {}      # Finished Downloads
        self.downloads = {}     # All Downloads

    def fetch(self, url):
        """Fetch the MusicMP3.ru URL

        @since  0.1.0
        @udpate 0.1.2
        """
        response = requests.get(url, headers=self.h)
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

    #
    # CALLBACK METHODs
    #
    def _cb_status(self, ticket, *args):
        """Callback

        @since  0.1.2
        """
        pass

    def _cb_success(self, ticket):
        """Callback

        @since  0.1.2
        """
        if len(self.tickets) == 0:
            return self.stop()
        return True

    def _cb_error(self, ticket):
        """Callback

        @since  0.1.2
        """
        pass

    #
    # HELPER METHODs
    #
    def _format(self, string, track):
        """Helper Method, which converts the config Path / Dir

        @since  0.1.2
        """
        for key in track:
            string = string.replace("%" + key + "%", track[key])
        return string

    #
    # DOWNLOADER METHODs
    #
    def download(self, ticket):
        """This method takes on the main task: Downloading!

        @since  0.1.0
        @update 0.1.2
        """
        if ticket not in self.downloads:
            return False

        # Abort - Stop and Error
        if not self.running:
            self.callback(ticket, (None, "Abort"))
            return False

        # Get Track and Track Process
        track = self.downloads[ticket]
        if self.pool is not False and current_process() not in self.current:
            self.current[current_process()] = ticket

        # Prepare Folder
        path = os.path.join(self.path, self._format(self.c["dirname"], track))
        if not os.path.isdir(path):
            os.makedirs(path)
        file = os.path.join(path, self._format(self.c["filename"], track))

        # Get Music Track
        data = requests.get(self.li + ticket, headers=self.h, stream=True)
        if data.status_code != 200:
            self.callback(ticket, (False, str(data.status_code)))
            time.sleep(1.5)
            self.callback(ticket, (None, "Reload"))
            time.sleep(0.25)
            return self.download(ticket)

        # Check Music Track
        if os.path.isfile(file + ".mpeg") or os.path.isfile(file + ".mp3"):
            self.callback(ticket, (True, 200, "Finished"))
            if not self.pool:
                if len(self.tickets) > 0:
                    return self.handle()
                return self.stop()
            return ticket

        # Write Music Track
        size = 0
        with open(file + ".mpeg", "wb") as f:
            for chunk in data.iter_content(chunk_size=2048):
                if not self.running:
                    f.close()
                    os.remove(file + ".mpeg")
                    break
                if chunk:
                    f.write(chunk)
                    size += len(chunk)
                length = data.headers["content-length"]
                percent = round(size*100 / int(length), 2)
                self.callback(ticket, (True, 206, percent))

        # Abort - Stop and No-Error
        if not self.running and not os.path.isfile(file + ".mpeg"):
            self.callback(ticket, (None, "Abort"))
            return False

        # Convert Music Track
        self.callback(ticket, (None, "Converting..."))
        if self.convert(file):
            self.callback(ticket, (True, 200, "Finished"))
        else:
            self.callback(ticket, (False, "FFMPEG failed"))

        # Download Finished
        self.finished[ticket] = track
        del self.downloads[ticket]
        del self.tickets[self.tickets.index(ticket)]

        # Return
        if not self.pool:
            if len(self.tickets) > 0:
                return self.handle()
            return self.stop()
        return ticket

    def convert(self, file):
        """Convert downloaded .mpeg into .mp3 with FFMPEG

        @since  0.1.2
        """
        command = ["ffmpeg", "-y", "-i", file + ".mpeg", file + ".mp3"]

        # Existing FFMPEG
        if subprocess.getstatusoutput("ffmpeg -h")[0] == 0:
            NULL = open(os.devnull, "w")
            test = subprocess.check_call(command, stdout=NULL,
                                         stderr=subprocess.STDOUT)

        # OnBoard FFMPEG (Windows-Only)
        elif os.name == "nt":
            if getattr(sys, "frozen", False):
                path = os.path.dirname(os.path.realpath(sys.executable))
            else:
                path = os.path.dirname(os.path.realpath(__file__))
            command[0] = os.path.join(path, "ffmpeg", "ffmpeg")
            test = subprocess.check_call(command, shell=True)

        # Return
        if test == 0:
            if "NULL" in locals():
                NULL.close()
            os.remove(file + ".mpeg")
            return True
        return False

    def start(self, callback=None, pool=False):
        """Starts the Download Script and initialises the multiprocessing Pool

        @since  0.1.0
        @update 0.1.2
        """
        if len(self.downloads) == 0 or self.running is True:
            return False
        self.running = True

        # Set Callable  and Tickets
        if callable(callback):
            self.callback = callback
        else:
            self.callback = self._cb_status
        self.tickets = list(self.downloads.keys())

        # Single Processing
        if pool is False or os.cpu_count() == 1:
            return self.handle(False)
        return self.handle(True)

    def handle(self, pool=False):
        """Handles the Download Calls and assigns Download Tickets

        @since  0.1.0
        @update 0.1.2
        """
        if pool is False:
            ticket = self.tickets[0]
            return self.download(ticket)

        self.pool = Pool(2)
        for ticket in self.tickets:
            self.pool.apply_async(self.download, (ticket,),
                                  callback=self._cb_success,
                                  error_callback=self._cb_error)
        return True

    def stop(self):
        """Stops the Download Script and terminates the Pool if needed.

        @since  0.1.0
        @update 0.1.2
        """
        if not self.running:
            return True
        self.running = False

        # Multi-Processing
        if self.pool:
            if len(self.current) > 0:
                self.pool.terminate()
            else:
                self.pool.close()
                self.pool.join()

        # Reset Variables
        self.pool = False
        self.tickets = []
        self.current = {}
        return True


def main():
    """Main Instance Function / CLI

    @since  0.1.0
    @update 0.1.2
    """
    parser = argparse.ArgumentParser(
            description="Download tracks from MusicMP3.ru"
    )
    parser.add_argument("URL",
                        help="The MusicMP3.ru URL")
    parser.add_argument("-p", "--path",
                        help="The download path for the Tracks")
    parser.add_argument("-f", "--fetchonly",
                        help="Just get the respective download links",
                        action='store_true')

    # Parse Arguments
    con = parser.parse_args()
    con.URL = MMP3_URL(con.URL)
    if con.URL is False:
        error = "The passed MusicMP3.ru URL is invalid!"
        parser.error(error)

    if con.path is not None and os.path.isdir(con.path) is False:
        error = "The Download Path doesn't exist os isn't writable!"
        parser.error(error)

    # Handle Action
    mmp3 = MMP3(dict([("path", con.path)]))
    tracks = mmp3.fetch(con.URL)

    if tracks is False or len(tracks) == 0:
        error = "The MusicMP3.ru URL is invalid or doesn't contain any Track!"
        parser.error(error)

    if con.fetchonly is True:
        for track in tracks:
            print(mmp3.li + track["hash"])
        print("\n")
        parser.exit(200, "Links have been successfully fetched!")

    for track in tracks:
        mmp3.start(lambda x,y: progress(track,y), False)
    parser.exit(200)


def progress(track, status):
    """CLI ProgessBar Function

    @since  0.1.0
    @update 0.1.2
    """
    if status[0] is True:
        if status[1] == 200:
            title = track["album"] + " - " + track["title"]
            sys.stdout.write("\r%s has been successfully downloaded\n" % title)
        else:
            title = track["album"] + " - " + track["title"]
            split = str(status[2]).split(".")
            split = (title, split[0], "{:<02d}".format(int(split[1])))
            sys.stdout.write("\r%s - %s.%s %%" % split + " " * 30)
            sys.stdout.write("\b" * 30)
    elif status[0] is False:
        sys.stdout.write("Error %d" % status[1] + " " * 30)
        sys.stdout.write("\b" * 30)
    else:
        sys.stdout.write("\r%s" % status[1] + " " * 30)
        sys.stdout.write("\b" * 30)
    sys.stdout.flush()


if __name__ == "__main__":
    main()
