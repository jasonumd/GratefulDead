# Jason Evans
# 2025-05-15
# Python script to read a path and song title from a | separated file.
# Song title is set.
#
# Command Line Arguments:
# 1: String representing drive letter. Example "D"
# 2: int representing number of pad characters in flac filename before date. Example: gd1986-12-15 = 2
# 3: int representing if this is a Grateful Dead (1) or Jerry Garcia (0) lookup
# 4: int. (1) for simple set, meaning just use | separated file (no database, etc.). (0) for pulling date from folder name
#    and using database.
# 5: Path to | separated file.

import sys
import os
import sqlite3 #Should work after sqlite3 installed
import pathlib #pip install pathlib
import datetime
import music_tag #pip install music-tag
from pathlib import Path #pip install pathlib

if (len(sys.argv) - 1) != 5:
    print("This script requires 4 command line arguments.")
    sys.exit()

Drive = str(sys.argv[1])
NumPadChars = int(sys.argv[2]) #int representing number of pad characters in flac filename before date. Example: gd1986-12-15 = 2
GD = int(sys.argv[3]) #int representing if this is a Grateful Dead (1) or Jerry Garcia (0) lookup
SimpleSet = int(sys.argv[4]) #int. (1) for simple set, meaning just use | separated file (no database, etc.). (0) for pulling date from folder name
                             #and using database.
infile = sys.argv[5] #| separated file with path and song title

#Database
db = "JerryBase.db"

if not os.path.exists("logs"): os.makedirs("logs")
skipped_log = "logs\\skipped.txt"
if os.path.exists(skipped_log): os.remove(skipped_log)
SHNID_log = "logs\\SHNID_log.txt"
if os.path.exists(SHNID_log): os.remove(SHNID_log)
file_error = "logs\\file_error.txt"
if os.path.exists(file_error): os.remove(file_error)
date_not_found_log = "logs\\date_not_found_log.txt"
if os.path.exists(date_not_found_log): os.remove(date_not_found_log)
song_not_found_log = "logs\\song_not_found_log.txt"
if os.path.exists(song_not_found_log): os.remove(song_not_found_log)
too_many_songs_log = "logs\\too_many_songs_log.txt"
if os.path.exists(too_many_songs_log): os.remove(too_many_songs_log)

def write_line(file, line):
    f = open(file, 'a')
    
    line = line.strip('\r')
    line = line.strip('\n')
    line += '\n'
    f.write(line)
    f.close()

with open(infile, "r") as file:
    con = sqlite3.connect(db) #DB connection
    cur = con.cursor()
    YearEcho = ""
    
    for line in file:
        items = line.split('|')
        
        songfile = str(items[0]).replace("[drive]", Drive)
        songtitle = str(items[1])
        songsegue = str(items[2]).strip('\n')
        
        try:
            audio = music_tag.load_file(songfile)
        except FileNotFoundError:
            write_line(file_error, songfile)
            continue
        
        #Always just using the song title from the CSV.
        NewSongTitle = songtitle
        segue = ""
        
        if SimpleSet == 1:
            if songsegue == ">": 
                segue = " >"
                
            audio['TITLE'] = songtitle + segue
            audio.save()
            
            continue
        
        #Pull show folder in order to isolate date and SHNID
        ShowFolder = pathlib.PurePath(songfile).parent.name
                
        #Attempt to pull SHNID from folder name in order to keep a record.
        words = ShowFolder.split(".")
        SHNID = ""
        
        for word in words:
            try:
                SHNID_int = int(word)
                SHNID = str(SHNID_int)
                write_line(SHNID_log, SHNID)
            except ValueError:
                continue
        
        #Get date from song file name.
        #gd1971-02-20 for example
        ParsedDate = ShowFolder[NumPadChars:NumPadChars + 10]
        DateFormat = "%Y-%m-%d"
        
        try:
            dt = datetime.datetime.strptime(ParsedDate, DateFormat) #parse(DateFolder[:(NumPadChars + 10)], fuzzy = False) #Date is 10 chars
        except:
            write_line(date_not_found_log, songfile)
            
            #This usually means the date in the folder name has an XX or 00 in it, meaning unknown.
            #Just set based on file.
            if songsegue == ">": 
                segue = " >"
                
            audio['TITLE'] = songtitle + segue
            audio.save()
            
            continue
        
        year = dt.year
        month = dt.month
        day = dt.day
        
        #Echo new years
        if YearEcho != str(year):
            YearEcho = str(year)
            print(YearEcho)        
        
        #Handle Early/Late shows
        EarlyLate = None
        result = None
        
        if "early" in ShowFolder.lower() and "late" in ShowFolder.lower(): #Rare instance where filename contains both early and late
            write_line(skipped_log, songfile)
            
            #Similar to no date found, just use file.
            audio['TITLE'] = songtitle
            audio.save()
            
            continue
        elif "early" in ShowFolder.lower():
            EarlyLate = "EARLY"
        elif "late" in ShowFolder.lower():
            EarlyLate = "LATE"

        if EarlyLate is None:
            sql = "SELECT songs.name, event_songs.segue " \
                  "FROM acts INNER JOIN (songs INNER JOIN ((events INNER JOIN event_sets ON events.id = event_sets.event_id) INNER JOIN event_songs ON event_sets.id = event_songs.event_set_id) ON songs.id = event_songs.song_id) ON acts.id = events.act_id " \
                  "WHERE event_sets.soundcheck=0 AND acts.gd=? AND events.year=? AND events.month=? AND events.day=? AND songs.name=? " \
                  "ORDER BY event_sets.seq_no, event_songs.seq_no"
            
            result = cur.execute(sql, (GD, year, month, day, songtitle)).fetchall()
        else:
            sql = "SELECT songs.name, event_songs.segue " \
                  "FROM acts INNER JOIN (songs INNER JOIN ((events INNER JOIN event_sets ON events.id = event_sets.event_id) INNER JOIN event_songs ON event_sets.id = event_songs.event_set_id) ON songs.id = event_songs.song_id) ON acts.id = events.act_id " \
                  "WHERE acts.gd=? AND events.year=? AND events.month=? AND events.day=? AND event_sets.soundcheck=0 AND songs.name=? AND events.early_late=? " \
                  "ORDER BY event_sets.seq_no, event_songs.seq_no"

            result = cur.execute(sql, (GD, year, month, day, songtitle, EarlyLate)).fetchall()
        
        
        if len(result) == 0: #No songs
            write_line(song_not_found_log, songfile + '|' + songtitle)
            
            #This is probably a title that isn't an actual song, for example 'Banter'.
            #Could also be a line that has '>' in the middle since it's actually multiple songs segued.
            #I'm deciding to pull forward segues from the original titles.
            if songsegue == ">": 
                segue = " >"

        elif len(result) > 1: #Too many songs
            write_line(too_many_songs_log, songfile + '|' + songtitle)
            
            #This is usually a case where a song is played twice, for example a reprise.
            #The issue is that I can't figure out an accurate way to handle the second segue.
            #I'm deciding to pull forward segues from the original titles.
            if songsegue == ">": 
                segue = " >"
             
        else:
            row = result[0]

            if row[1] == 1:
                segue = " >"
            else:
                if songsegue == ">": #I'm deciding to pull forward segues from the original titles.
                    segue = " >"
        
        audio['TITLE'] = NewSongTitle + segue
        audio.save()