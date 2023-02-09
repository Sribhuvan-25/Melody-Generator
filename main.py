import os
import music21 as m21
import json
# import tensorflow.keras as keras
import tensorflow as ts
import keras
import numpy as np

SONGS_PATH = "Data/test"
ACCEPTABLE_DURATIONS = [0.25, 0.5, 0.75, 1.0, 1.5, 2, 3, 4]
SAVE = "Dataset"
SINGLE_FILE_PATH = "single_file"
LENGTH = 64
DICT_PATH = "dict.json"

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
        
        # Transpoing to C maj / A min
        song = transpose(song)

         # Encoding
        encoded_song = encode_song(song)

        SAVE_songs = os.path.join(SAVE, str(i))
        with open(SAVE_songs, "w") as fp:
            fp.write(encoded_song)
    
def load(path):
    with open(path, "r") as fp:
        song = fp.read()
        return song

def create_single_file(dataset_path, file_path, sequence_len):
    delimeter = "/ " * sequence_len
    songs = ""

# Adding delimeters after loading the encoded songs
    for path, subdir, files in os.walk(dataset_path):
        for file in files:
            filePath = os.path.join(path, file)
            song = load(filePath)
            songs = songs + song + " " + delimeter
    # Take everything apart from the last character which is a space
    songs = songs[:-1]

    with open(file_path, "w") as fp:
        fp.write(songs)
    
    return songs

def mapping(songs, dict_path):
    
    dict = {}

    songs = songs.split()
    uniqueValues = list(set(songs))

    for i, el in enumerate(uniqueValues):
        dict[el] = i
    
    with open(dict_path, "w") as fp:
        json.dump(dict, fp, indent=2)

# Converting the song to a list of integers
def convert_songs(songs):

    intList = []    

    # Mapping List
    with open(DICT_PATH, "r") as fp:
        dict = json.load(fp)
    
    # Converting string to list
    songs = songs.split()

    # Mapping every symbol in the songs list to int
    for el in songs:
        intList.append(dict[el])
    
    return intList

# Generating training sequences, which are a subsets of time series music representation
def training_sequence(sequence_length):
    
    songs = load(SINGLE_FILE_PATH)
    mapped_songs = convert_songs(songs)

    inputs = []
    targets = []

    # Generating sequences
    # Predicting the next musical event in the melody
    # 64 time steps for each training sample
    total_sequences = len(mapped_songs) - sequence_length
    for i in range(total_sequences):
        # Ex: [1,2,3,4] [i: [1,2] -> t: [3]] [[2,3] -> [4]] 
        inputs.append(mapped_songs[i:i+sequence_length])
        targets.append(mapped_songs[i+sequence_length])
    
    # One Hot Ecnoding
    # Inputs is a 2D array, (total_sequences, sequence_length, unique_elements)
    # [[0,1,2],[1,1,2]] -> [[[1,0,0], [0,1,0], [0,0,1]], []]
    #                           0         1        2
    unique_elements = len(set(mapped_songs))
    inputs = keras.utils.to_categorical(inputs, num_classes=unique_elements)
    targets = np.array(targets)

    return inputs, targets


def main():
    preprocess(SONGS_PATH)
    songs = create_single_file(SAVE, SINGLE_FILE_PATH,  LENGTH)
    mapping(songs, DICT_PATH)
    inputs, targets = training_sequence(LENGTH)
    print(inputs)
    print(targets)

main()
