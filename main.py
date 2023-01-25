import os
import music21 as m21

songs_path = "Data/test"
acceptable_durations = [0.25, 0.5, 0.75, 1.0, 1.5, 2, 3, 4]

def load_songs(datset_path):
    songsList = []
    for path,subdir,files in os.walk(datset_path):
        for file in files:
            if file[-3:] == "krn":
                songsList.append(m21.converter.parse(os.path.join(path, file)))
    return songsList

def filter_durations(song, acceptable_durations):

    for note in song.flat.notesAndRests:
        if note.duration.quarterLength not in acceptable_durations:
            return False
    return True

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
    
    # Transposition
    transpose_song = song.transpose(interval)
    return transpose_song

def preprocess(dataset_path):
    songs = load_songs(dataset_path)
    print(f"# songs loaded = {len(songs)}")
    
    for song in songs:
        if not filter_durations(song, acceptable_durations):
            continue

        song = transpose(song)


preprocess(songs_path)

