Changelog
=========

Version 0.1.2 - Alpha
---------------------
-   Add: A Clear TrackList Action Button
-   Add: Right-Click Context-Menu for the input field
-   Add: 'Clear', 'Cut', 'Copy', 'Paste', 'Select All' context menu functions
-   Add: A new download-ticket system, adapted to the new multiprocessing.dummy
-   Add: Callback methods `_cb_status` (custom), `_cb_success` and `_cb_error`
-   Add: New .ini Configuration with 3 settings: "path", "dirname" and "filename"
-   Add: New `_format` method, optimized for the new ini-settings
-   Update: Check if file already exists.
-   Update: Add icon to the setup.py Executable class
-   Update: FFMPEG Converter Call has been moved to an own method
-   Update: Rewritten multiprocessing.dummy implementation
-   Bugfix: "Stop Download" crashes the tk environment, based on the ugly implementation of multiprocessing.dummy
-   Pythonic: Follow some PEP 8 Standards / Rules

Version 0.1.1 - Alpha
---------------------
-   Add: A Favicon and Icons for the download button
-   Add: Bind MouseWheel to Canvas Object
-   Add: "Enter" and "Leave" effect bind to both buttons
-   Add: Display a Download Text-Counter
-   Add: Show Name of the Artist in the Track Item List
-   Update: Hide output from FFMPEG by writing it to an devnull object
-   Update: Some smart design changes (tkinter is a bitch)
-   Update: Changed passed variable style on the MMP3 callback function
-   Update: Changed "#-Comment" to DocString conform Commenting
-   Update: The respective strings
-   Update: The download button disables itself after each track has been downloaded
-   Bugfix: Duplicate URL check doesn't stored the passed URLs
-   Bugfix: Clear "Previous" console line
-   Bugfix: Missing Exit after CLI-Mode has finished downloading.
-   Pythonic: Don't use `from ... import *` at all

Version 0.1.0 - Alpha
---------------------
-   First Alpha Version