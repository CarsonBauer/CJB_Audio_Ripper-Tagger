# CJB_Audio_Ripper-Tagger
Python script I made to rip and tag audio from a CD drive. Intended for use on Linux systems. Utilizes cdparanoia to rip from mounted CD drive and saves the audio files in the WAV format. These files are then encoded in MP3 and queries are made to the MusicBrainz API to retireve tag info, which are embedded in the audio files using Mutagen. When finished, this script will create an Artist/Album directory structure in the current working directory which will contain the audio files.

# Dependencies
- cdparanoia
- Mutagen Python library
- Python runtime

# Usage
**python get_albums.py [Artist Name] -a [Album Name]**

Run the script by passing in the name of the artist followed by the name of the album you are ripping. A prompt will then show listing all different releases of the given album from the given artist. Select the index of the release to select the release that is being ripped.
