import requests, sys, os, mutagen
from mutagen.mp3 import EasyMP3

# Get release cooresponding with given album name and artist name
def get_albums(album, artist):

    # Encode album and artist info and format URL string
    encoded_album = album.replace(" ", "%20")
    encoded_artist = artist.replace(" ", "%20")
    mb_album_url = "https://musicbrainz.org/ws/2/release/?query=release:%22{Album}%22%20AND%20artist:%22{Artist}%22&fmt=json".format(Album=encoded_album, Artist=encoded_artist)

    # Send GET request to API and convert response to JSON
    response = requests.get(mb_album_url)
    json_response = response.json()

    return json_response

# Print out all releases in releases JSON object
def list_releases(releases):
    count = 0
    for release in releases["releases"]:
        name = "N/A" if not "release" in release else release["release"]
        country = "N/A" if not "country" in release else release["country"]
        date = "N/A" if not "date" in release else release["date"]
        tracks = "N/A" if not "track-count" in release else release["track-count"]

        print("[{Count}] {Release} - {Country} - {Date} - {Tracks}".format(Count=count, Release=release["title"], Country=country, Date=date, Tracks=release["track-count"]))
        count = count + 1

# Get all songs from given release ID
def get_songs(reid):
    mb_songs_url = "https://musicbrainz.org/ws/2/recording/?query=reid:{REID}&fmt=json".format(REID=reid)

    response = requests.get(mb_songs_url)
    json_response = response.json()

    return json_response

# List out songs in given songs JSON object
def list_songs(songs, reid):
    songs_formatted = []
    for recording in songs["recordings"]:
        release = list(filter(lambda x: x["id"] == reid, recording["releases"]))[0]
        songs_formatted.append({"title": recording["title"], "offset": release["media"][0]["track-offset"]})
        # print("{TITLE}, {OFFSET}".format(TITLE=recording["title"], OFFSET=release["media"][0]["track-offset"]))
    songs_formatted.sort(key=(lambda x: x["offset"]))
    return songs_formatted

# Rip audio, store in created directories, convert to mp3 and remove WAVE files if album does not yet exist
def rip_audio(artist, album, exists):
    if (exists == 0):
        if (os.system("cd \'{Artist}\'/\'{Album}\' && cdparanoia -XB".format(Artist=artist, Album=album)) != 0):
            return "ERROR: Cannot rip from CD reader"

        for file in os.listdir("{Artist}/{Album}".format(Artist=artist, Album=album)):
            if (os.system("cd \'{Artist}\'/\'{Album}\' && lame -b 320 {song}".format(song=file, Artist=artist, Album=album)) != 0):
                return "ERROR: Cannot rip from CD reader"

        if (os.system("cd \'{Artist}\'/\'{Album}\' && rm *.wav".format(Artist=artist, Album=album)) != 0):
            return "ERROR: Cannot remove .wav files"
        return "OK"
    else:
        print("Album already exists. Moving on to tagging.")
        return "OK"

# Create album and artist directories
def create_directories(artist, album):
    return os.system("if ! test -d \'{Artist}\'; then mkdir \'{Artist}\'; fi && mkdir \'{Artist}/{Album}\'".format(Artist=artist, Album=album))

# Tag albums with Artist and Album info
def tag_albums(artist, album, songs):
    count = 0
    dir_list = os.listdir("{Artist}/{Album}".format(Artist=artist, Album=album))
    dir_list.sort()
    for file in dir_list:
        file_path = "{Artist}/{Album}/".format(Artist=artist, Album=album) + file
        new_file_path = "{Artist}/{Album}/".format(Artist=artist, Album=album) + "{OFFSET} - {TITLE}".format(OFFSET=songs[count]['offset'], TITLE=songs[count]['title'])
        audio = EasyMP3(file_path)
        audio["Artist"] = artist
        audio["Title"] = songs[count]['title']
        audio["tracknumber"] = '{}/{}'.format(songs[count]['offset'] + 1, len(songs))
        audio["Album"] = album
        audio.save()
        #os.system("mv \'{OLD_PATH}\' \'{NEW_PATH}\'".format(OLD_PATH=file_path, NEW_PATH=new_file_path))
        count = count + 1

# Script driver (main)
def run_script():
    artist = ""
    album = ""
    artistName = True

    # Parse python arguments
    for i in range(1, len(sys.argv)):
        if (sys.argv[i] == "-a"):
            artistName = False
        elif artistName:
            if (i > 1):
                artist += " "
            artist += sys.argv[i]
        else:
            album += sys.argv[i]
            if (i < len(sys.argv) - 1):
                album += " "

    exists = create_directories(artist, album)
    rip_status = rip_audio(artist, album, 0)

    if (rip_status != "OK"):
        return "ERROR: Ripping process failed"

    releases = get_albums(album, artist)
    list_releases(releases)

    release_index = input("\nEnter release number: ")
    selected_release = releases["releases"][int(release_index)]

    songs = get_songs(selected_release["id"])
    songs_formatted = list_songs(songs, selected_release["id"])

    tag_albums(artist, album, songs_formatted)

    print(songs_formatted)

run_script()
