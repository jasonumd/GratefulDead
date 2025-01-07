# GratefulDead
Digitizing Grateful Dead data and making it freely available to all Deadheads.

Deadbase XI
Updated OCR was generated on the Deadbase XI scan using NAPS2. New PDF was exported as .txt using Adobe Reader. SHA-512 hashes of these files are included. I am currently working on getting Deadbase XI text into a sqlite database. This is forthcoming.

music_album_rename
This script allows you to rename the album of an entire library based on the 4 digit year in the .flac filename and the contents of the music.db sqlite database. The format the script uses is "YYYY-MM-DD Venue, Location2, Location2", but you can modify this as you prefer for your library preferences. The database is currently populated with all Grateful Dead shows.
Note: I only deal in 4-digit years and adapted my libary accordingly using Microsoft Windows PowerRename. I have my Grateful Dead library organized by year and used MP3Rename to set consistent year, Genre (Rock), Artist (Greatful Dead), and Album Artist (Grateful Dead) for all .flac files. As of now, I haven't touched track or comment fields.
Note2: I currently use Plex for my library and noticed an anomaly. There are multiple recordings for the same show. Plex seems to no always differentiate these as different albums when building its library. I'm looking into adding recording information to the album name in order to differentiate the multiple recordings. Perhaps prioritizing by who remixed the file.
