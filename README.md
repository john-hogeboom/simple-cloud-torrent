# simple-cloud-torrent
Provide cloud torrent service; users set folder names as magnet links, files torrented and uploaded.

User instructions:

1. Create Mega.nz account, provide host with your login information.
2. Wait for new folder 'TorrentToCloud' to appear in your Mega account
3. Create a new folder with the magnet link for your desired torrent as its name.
4. A folder with your completed download will appear.


Host instructions:

1. Install Megatools, 7Zip, Python 2.7, Deluge, deluge-console, and deluged.
2.  Add paths to these in config file, like this (substitute own file paths):
  
[file]
DelugeInstall: C:\Program Files (x86)\Deluge
MegatoolsInstall: C:\Users\Username\Downloads\megatools-1.9.97-win32
7ZipInstall: C:\Program Files\7-Zip
[other]
interval_seconds: 120
zip_files: True

Or, alternately, leave these fields blank if your path variable is set to include those directories (this should happen by default on Linux).

3 . Add all client's Mega username and password to the spreadsheet 'accounts.csv' (comma separated)

4 . Open Deluge, go to preferences > interface and disable Classic Mode, then restart Deluge and click 'Start Daemon'.

5 . Open a command prompt/terminal, change directory to the folder containing ttcd.py, and run the command 'python ttcd.py'
