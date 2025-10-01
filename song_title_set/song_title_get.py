# Jason Evans
# 2025-03-29
# Python script to export every flac song title to a | separated file.
# Directories are traversed recursively.
# 
# Command Line Arguments:
# 1: Output csv file name.
# 2: Top level directory path to rename. This script is recursive.

import sys
import os
import music_tag #pip install music-tag
from pathlib import Path #pip install pathlib

def traverse_directory(path):
    for root, dirs, files in os.walk(path):
        Folder = os.path.basename(root)
        
        for file in files:
            filepathname = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()
            filename =  Path(filepathname).stem
            
            if file_extension == ".flac" or file_extension == ".mp3":
                audio = music_tag.load_file(filepathname)
                title = audio['title']
                                
                print ("\n" + str(title))
                line = str(filepathname) + "|" + str(title)
                write_line(outfile, line)

def write_line(file, line):
    f = open(file, 'a')
    line = line.strip('\r')
    line = line.strip('\n')
    line += '\n'
    f.write(line)
    f.close()
    
if (len(sys.argv) - 1) != 2:
    print("This script requires 2 command line arguments.")
    sys.exit()

outfile = sys.argv[1] #Output file name
path = sys.argv[2] #Top level directory
if os.path.exists(outfile): os.remove(outfile)

traverse_directory(path)