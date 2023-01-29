import os
import music21 as m21

SONGS_PATH = "Data/test"
ACCEPTABLE_DURATIONS = [0.25, 0.5, 0.75, 1.0, 1.5, 2, 3, 4]
SAVE = "Dataset"

def load_songs(datset_path):
    songsList = []
    for path,subdir,files in os.walk(datset_path):
        for file in files:
            if file[-3:] == "krn":
                songsList.append(m21.converter.parse(os.path.join(path, file)))
    return songsList

def filter_durations(song, ACCEPTABLE_DURATIONS):

    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in ACCEPTABLE_DURATIONS:
            return False
    return True

# Changing the music data to time series representation
def encode_song(song, timeStamp = 0.25):

    encoded_list = []
    for event in song.flat.notesAndRests:

        if isinstance (event, m21.note.Note):
            symbol = event.pitch.midi
        
        if isinstance(event, m21.note.Rest):
            symbol = "r"
    
        steps = int(event.duration.quarterLength / timeStamp)
        for step in range(steps):
            if step == 0:
                encoded_list.append(symbol)
            else:
                encoded_list.append("_")

    encoded_list = " ".join(map(str, encoded_list))
    return encoded_list


def transpose(song):

    # music score has multiple parts
    parts = song.getElementsByClass(m21.stream.Part)
    partZero = parts[0].getElementsByClass(m21.stream.Measure)
    key = partZero[0][4]

    # Estimating key incase there isn't one
    if not isinstance(key, m21.key.Key):
        key = song.analyze("key")
    
    # Interval for transposition
    if key.mode == "major":
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("C"))
    elif key.mode == 'minor':
        interval = m21.interval.Interval(key.tonic, m21.pitch.Pitch("A"))
    
    transpose_song = song.transpose(interval)
    return transpose_song
    
    
def preprocess(dataset_path):
    songs = load_songs(dataset_path)
    print(f"# songs loaded = {len(songs)}")
    
    for i, song in enumerate(songs):

        # Filtering durations
        if not filter_durations(song, ACCEPTABLE_DURATIONS):
            continue
        
        # Transpoing
        song = transpose(song)

         # Encoding
        encoded_song = encode_song(song)

        SAVE_songs = os.path.join(SAVE, str(i))
        with open(SAVE_songs, "w") as fp:
            fp.write(encoded_song)


preprocess(SONGS_PATH)

