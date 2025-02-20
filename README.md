# **GratefulDead**
Digitizing Grateful Dead data and making it freely available to all Deadheads.

## **Deadbase XI**
Updated OCR was generated on the Deadbase XI scan using NAPS2. New PDF was exported as .txt using Adobe Reader. SHA-512 hashes of these files are included.  

## **music_album_rename**
This script allows you to rename the album of an entire library based on the date in the .flac filename and the contents of the JerryBase.db sqlite database. The format the script uses is "YYYY-MM-DD (source SHNID) Venue, Location1, Location2", but you can modify this as you prefer for your library preferences. The database is courtesy of the db admin for JerryBase.com and it contains all information for Grateful Dead and Jerry Garcia related shows. Obtaining a dump of this database was a lifesaver, especially for tagging JGB shows.  
  
**Note:** I only deal in 4-digit years and adapted my libary accordingly using Microsoft Windows PowerRename. If you prefer keeping the 2-digit year you will have to make some changes. I have my Grateful Dead library organized by year and used MP3Rename to set consistent year, Genre (Rock), Artist (Greatful Dead), and Album Artist (Grateful Dead) for all .flac files. As of now, I haven't touched track or comment fields.
