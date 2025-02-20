# Jason Evans
# 2025-02-08
# Python script to rename music albums. Created for Grateful Dead but can be adapted for any artist.
# I only deal in 4-digit years. My library was adapted for such.
# 
# Command Line Arguments:
# 1: int representing running the script in trial mode. 1 = trial mode (album info won't be written). 0 = Full Send.
# 2: int representing number of pad characters in flac filename before date. Example: gd1986-12-15 = 2
# 3: int representing if this is a Grateful Dead (1) or Jerry Garcia (0) lookup
# 4: Top level directory path to rename. This script is recursive.

#pip install mutagen
#pip install pathlib
#pip install python-dateutil
#install sqlite3

import sys
import os
import sqlite3 #Should work after sqlite3 installed
from mutagen.flac import FLAC #pip install mutagen
from pathlib import Path #pip install pathlib
from dateutil.parser import parse #pip install python-dateutil

def traverse_directory(path):
    con = sqlite3.connect(db) #DB connection
    cur = con.cursor()
    
    for root, dirs, files in os.walk(path):
        Folder = os.path.basename(root)
        print("\n" + Folder)
        
        #Attempt to pull SHNID from folder name
        words = Folder.split(".")
        SHNID = ""
        
        for word in words:
            try:
                SHNID_int = int(word)
                SHNID = str(SHNID_int)
            except ValueError:
                continue
        
        if not SHNID:
            write_line(no_shnid_log, Folder)
        
        #Get date from folder name.
        #gd1971-02-20 for example
        try:
            dt = parse(Folder[:(NumPadChars + 10)], fuzzy = True) #Date is 10 chars
        except:
            write_line(date_not_found_log, Folder)
            continue

        year = dt.year
        month = dt.month
        day = dt.day
        
        #Handle multiple versions of same day. There can exist > 1 aud, sbd, or sbd Miller recording for same show.
        Version = ""
        
        if "sbd" in Folder.lower():
            Version = " (sbd"
        elif "aud" in Folder.lower():
            Version = " (aud"
        elif "nak" in Folder.lower():
            Version = " (aud"
        elif "sony" in Folder.lower():
            Version = " (aud"
        elif "akg" in Folder.lower():
            Version = " (aud"
        elif "senn" in Folder.lower():
            Version = " (aud"
        elif "fm" in Folder.lower():
            Version = " (fm"
        elif "tv" in Folder.lower():
            Version = " (tv"
        elif "fob" in Folder.lower():
            Version = " (fob"
        elif "studio" in Folder.lower():
            Version = " (studio"
        elif "gmb" in Folder.lower():
            Version = " (gmb"
        elif "pa" in Folder.lower():
            Version = " (pa"
        elif "mtx" in Folder.lower():
            Version = " (mtx"
        else:
            write_line(no_version_log, Folder)

        #Add Miller
        if "miller" in Folder.lower():
            if Version:
                Version += " Miller"
            else:
                Version = " (Miller"
        
        #Strategically add SHNID
        if Version:
            if SHNID:
                SHNID = " " + SHNID
            
            Version += SHNID + ")"
        elif SHNID:
            Version = " (" + SHNID + ")"

        #Handle Early/Late shows
        EarlyLate = ""
        
        if "early" in Folder.lower() and "late" in Folder.lower(): #Rare instance where filename contains both early and late
            EarlyLate = " (Early/Late Show)"
            write_line(early_and_late_log, Folder)
        elif "early" in Folder:
            EarlyLate = " (Early Show)"
            write_line(early_log, Folder)
        elif "late" in Folder:
            EarlyLate = " (Late Show)"
            write_line(late_log, Folder)
        
        #                    0           1           2            3            4            5           6             7              8
        sql = "SELECT acts.name, events.id, events.year, events.month, events.day, venues.name, venues.city, venues.state, venues.country " \
              "FROM venues INNER JOIN (acts INNER JOIN events ON acts.id = events.act_id) ON venues.id = events.venue_id " \
               "WHERE events.year=? AND events.month=? AND events.day=? and acts.gd=?;"
        
        #sql = "SELECT Artists.artist, Shows.year, Shows.month, Shows.day, Venues.venue, Venues.location1, Venues.location2 " \
        #      "FROM Venues INNER JOIN (Artists INNER JOIN Shows ON Artists.artist_id = Shows.artist_id_fk) ON Venues.venue_id = Shows.venue_id_fk " \
        #      "WHERE Artists.artist=? AND Shows.year=? AND Shows.month=? AND Shows.day=?;"
        
        cur.execute(sql, (year, month, day, GD))
        result = cur.fetchall();
        
        if len(result) == 0: #Need to know unknown venues
            write_line(date_not_found_log, Folder)
            continue
        elif len(result) > 0:
            row = None
            
            if len(result) == 1:
                row = [(value if value is not None else '' ) for value in result[0]] #First row since using fetchall
            else:
                print("\nMultiple Database entries for folder " + Folder)
                i=0
                
                #Look for case of early/late shows where you will be presented with 2 identical options.
                row0compare = None
                row1compare = None
                
                for row in result:
                    processed_row = [(value if value is not None else '' ) for value in row]
                    
                    if i == 0:
                        row0compare = processed_row[0] + ", " + processed_row[5] + ", " + processed_row[6] + ", " + processed_row[7] + ", " + processed_row[8]
                    elif i == 1:
                        row1compare = processed_row[0] + ", " + processed_row[5] + ", " + processed_row[6] + ", " + processed_row[7] + ", " + processed_row[8]
                    
                    print(str(i) + ": " + processed_row[0] + ", " + processed_row[5] + ", " + processed_row[6] + ", " + processed_row[7] + ", " + processed_row[8])
                    i += 1
                
                print(str(i) + ": Skip")
                
                selection = None
                selection_int = None
                
                if len(result) == 2 and (row0compare == row1compare):
                    print("Entries are the same, selecting 0.")
                    selection = 0
                else:
                    selection = input("Which one would you like? ")
                    
                try:
                    selection_int = int(selection)
                except:
                    Print("Invalid entry. Skipping")
                    write_line(skipped_folder, Folder)
                    continue
                
                if (selection_int < 0) or (selection_int > i):
                    Print("Invalid entry. Skipping")
                    write_line(skipped_folder, Folder)
                    continue
                elif selection_int == i:
                    write_line(skipped_folder, Folder)
                    continue
                else:
                    row = result[selection_int]
                        
            #Handle Canada
            StateOrCanada = row[7]
            if row[7] is None:
                StateOrCanada = row[8]
            
            artist = row[0]
            albumnew = str(row[2]) + "-" + str(row[3]).zfill(2) + "-" + str(row[4]).zfill(2) + Version + " " + row[5] + EarlyLate + ", " + row[6] + ", " + StateOrCanada
            print (artist)
            print (albumnew)
        
            for file in files:
                filepathname = os.path.join(root, file)
                file_extension = os.path.splitext(file)[1].lower()
                filename =  Path(filepathname).stem
                
                if file_extension == ".flac":
                    audio = FLAC(filepathname)
                    
                    if TrialMode == 0:
                        title = ""
                        date = ""
                        tracknumber = ""
                        genre = ""
                        comment = ""
                        
                        try:
                            title = audio['title']
                        except:
                            continue
                            
                        try:
                            date = audio['date']
                        except:
                            continue
                            
                        try:
                            tracknumber = audio['tracknumber']
                        except:
                            continue
                            
                        try:
                            genre = audio['genre']
                        except:
                            continue
                            
                        try:
                            comment = audio['comment']
                        except:
                            continue
                        
                        audio.delete()
                        audio.save()
                        
                        audio['artist'] = artist
                        audio['albumartist'] = artist
                        audio['album'] = albumnew
                        
                        if title != "":
                            audio['title'] = title
                        
                        if date != "":
                            audio['date'] = date
                        
                        if tracknumber != "":
                            audio['tracknumber'] = tracknumber
                        
                        if genre != "":
                            audio['genre'] = genre
                            
                        if comment != "":
                            audio['comment'] = comment
                        
                        audio.save()
                elif file_extension == ".shn" or file_extension == ".mp3":
                    write_line(nonflac_log, filepathname)

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
GD = sys.argv[3] #GD=1, JG=0
path = sys.argv[4] #Top level directory

#Database
db = "JerryBase.db"

#Log Files
nonflac_log = "logs\\nonflac_log.txt"
early_and_late_log = "logs\\early_and_late_log.txt"
early_log = "logs\\early_log.txt"
late_log = "logs\\late_log.txt"
date_not_found_log = "logs\\date_not_found_log.txt"
no_version_log = "logs\\no_version_log.txt"
no_shnid_log = "logs\\no_shnid_log.txt"
multiple_records = "logs\\multiple_records.txt"
skipped_folder = "logs\\skipped_folder.txt"
if not os.path.exists("logs"): os.makedirs("logs")
if os.path.exists(nonflac_log): os.remove(nonflac_log)
if os.path.exists(early_and_late_log): os.remove(early_and_late_log)
if os.path.exists(early_log): os.remove(early_log)
if os.path.exists(late_log): os.remove(late_log)
if os.path.exists(date_not_found_log): os.remove(date_not_found_log)
if os.path.exists(no_version_log): os.remove(no_version_log)
if os.path.exists(no_shnid_log): os.remove(no_shnid_log)
if os.path.exists(multiple_records): os.remove(multiple_records)
if os.path.exists(skipped_folder): os.remove(skipped_folder)

traverse_directory(path)
