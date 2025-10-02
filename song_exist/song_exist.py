# Jason Evans
# 2025-08-07
# Python script that recursively scans folders for .flac files and checks if they're in songs.txt.
#
# Command Line Arguments:
# 1: Top level directory path to search. This script is recursive.

import os
import sys
import string
import sqlite3 #Should work after sqlite3 installed
from pathlib import Path #pip install pathlib
import music_tag #pip install music-tag

if (len(sys.argv) - 1) != 1:
    print("This script requires 1 command line argument. Read the header and try again.")
    sys.exit()

path = sys.argv[1] #Top level directory path to rename. This script is recursive.

#Database
db = "JerryBase.db"
con = sqlite3.connect(db) #DB connection
cur = con.cursor()
    
for root, dirs, files in os.walk(path):
    for file in files:
        filepathname = os.path.join(root, file)
        file_extension = os.path.splitext(file)[1].lower()
        filename =  Path(filepathname).stem
        
        if file_extension == ".flac":
            audio = music_tag.load_file(filepathname)
            
            #First I'm going capitalize the first letter of each word and save.
            #strTemp = str(audio['TITLE'])
            #audio['TITLE'] = " ".join((w[0].upper() + w[1:]) for w in strTemp.split())
            #audio.save()
            
            songtitle = str(audio['TITLE']).rstrip(" >")
    
            sql = "SELECT songs.* FROM songs WHERE songs.name=?"
            
            result = cur.execute(sql, (songtitle,)).fetchall()
            
            if len(result) == 0:
                print(filepathname + " :: " + songtitle)