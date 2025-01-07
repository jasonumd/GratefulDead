# Jason Evans
# 2025-01-07
# Python script to rename music albums. Created for Grateful Dead but can be adapted for any artist.
# I only deal in 4-digit years. My library was adapted for such.
# 
# Command Line Arguments:
# 1: int representing running the script in trial mode. 1 = trial mode (album info won't be written). 0 = Full Send.
# 2: int representing number of pad characters in flac filename before date. Example: gd1986-12-15 = 2
# 3: string representing artist name to look up in sqlite database. "Grateful Dead"
# 4: Top level directory path to rename. This script is recursive.

import sys
import os
from mutagen.flac import FLAC
import sqlite3
from pathlib import Path
from dateutil.parser import parse

def traverse_directory(path):
    con = sqlite3.connect(db) #DB connection
    cur = con.cursor()

    for root, dirs, files in os.walk(path):
        for file in files:
            filepath = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()

            if file_extension == ".flac":
                EarlyLate = ""

                audio = FLAC(filepath)
                filename =  Path(filepath).stem
                album = str(audio["album"]) #Existing album name
                
                #gd1971-02-20 for example
                dt = parse(filename[:(NumPadChars + 10)], fuzzy = True) #Date is 10 chars
                year = dt.year
                month = dt.month
                day = dt.day

                if "early" in album.lower() or "late" in album.lower(): #I already handled this manually
                    continue
                
                if "early" in filepath.lower() and "late" in filepath.lower(): #Rare instance where filename contains both early and late
                    write_line(early_and_late_log, filepath)
                    print("early and late")
                    continue
                
                elif "early" in filepath:
                    EarlyLate = " (Early Show)"
                    write_line(early_log, filepath)
                    print("early")
                
                elif "late" in filepath:
                    EarlyLate = " (Late Show)"
                    write_line(late_log, filepath)
                    print("late")

                sql = "SELECT Artists.artist, Shows.year, Shows.month, Shows.day, Venues.venue, Venues.location1, Venues.location2 " \
                      "FROM Venues INNER JOIN (Artists INNER JOIN Shows ON Artists.artist_id = Shows.artist_id_fk) ON Venues.venue_id = Shows.venue_id_fk " \
                      "WHERE Artists.artist=? AND Shows.year=? AND Shows.month=? AND Shows.day=?;"
                
                cur.execute(sql, (Artist, year, month, day))
                result = cur.fetchone();
                
                print(Artist + "|" + str(year)  + "|" + str(month)  + "|" + str(day))
                
                if result is None: #Need to know unknown venues
                    write_line(date_not_found_log, filepath)
                    print("None")
                else:
                    albumnew = str(result[1]) + "-" + str(result[2]).zfill(2) + "-" + str(result[3]).zfill(2) + " " + result[4] + EarlyLate + ", " + result[5] + ", " + result[6]
                    print (albumnew)
                    
                    if TrialMode == 0:
                        audio["album"] = albumnew
                        audio.save()

            elif file_extension == ".mp3":
                write_line(mp3_log, filepath)
                
    con.close();

def write_line(file, line):
    f = open(file, 'a')
    #print(file)
    line = line.strip('\r')
    line = line.strip('\n')
    line += '\n'
    f.write(line)
    f.close()

if (len(sys.argv) - 1) != 4:
    print("This script requires 4 command line argument. Read the header and try again.")
    sys.exit()

TrialMode = int(sys.argv[1])
NumPadChars = int(sys.argv[2])
Artist = sys.argv[3] #Artist to look up in sqlite database
path = sys.argv[4] #Top level directory

#Database
db = "Music.db"

#Log Files
mp3_log = "logs\\mp3_log.txt"
early_and_late_log = "logs\\early_and_late_log.txt"
early_log = "logs\\early_log.txt"
late_log = "logs\\late_log.txt"
date_not_found_log = "logs\\date_not_found_log.txt"
if not os.path.exists("logs"): os.makedirs("logs")
if os.path.exists(mp3_log): os.remove(mp3_log)
if os.path.exists(early_and_late_log): os.remove(early_and_late_log)
if os.path.exists(early_log): os.remove(early_log)
if os.path.exists(late_log): os.remove(late_log)
if os.path.exists(date_not_found_log): os.remove(date_not_found_log)

traverse_directory(path)
