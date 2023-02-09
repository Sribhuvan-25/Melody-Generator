def __init__(self, model_path="Network_model.h5"):
    
    self.model_path = model_path
    self.model = keras.models.load_model(model_path)

    with open(DICT_PATH, "r") as fp:
        self._mappings = json.load(fp)
    
    self._symbols = ["/"] * LENGTH

# Pieace of melody is a seed, which is given to the network form which network generates melody
# max_sequence_length is the max length of the seed, which equals to the sequence length (in this case 64)
# temp (Temperature) is a float values that influences how we sample output symbols from the probability distribution

def generateMelody(self,seed, num_steps, max_sequence_length, temp):

    # Starting seed start symbols
    seed = seed.split()
    melody = seed
    seed = self._symbols + seed

    # Map seed
    seed = [self._mappings[symbol] for symbol in seed]

    for _ in range(num_steps):
        
        # Making sure that seed length is within acceptable to length
        seed = seed[-max_sequence_length:]

        # One Hot Encoding
        seed_oneHot = keras.utils.to_categorical(seed, num_classes=len(self._mappings))
        # Example output -> (max_seqeunce_length, #symbols in the vocab (dict)) but the there should be a third dimension for keras to predict
        seed_oneHot = seed_oneHot[np.newaxis, ...]

        # Predicting
        probability_distribution = self.model.predict(seed_oneHot)[0]
        ouput = self._sample_with_temp(probability_distribution, temp)

        # Update seed (the output is added back as an input)
        seed.append(ouput)

        # Mapping values based off the encoding
        output_symbol = [key for key, value in self._mappings.items() if value == ouput][0]

        # Checking if the melody has ended
        if output_symbol == "/":
            break
        
        # update melody
        melody.append(output_symbol)

    return melody

def _sample_with_temperature(self, probability_distribution, temp):

    # temp -> infinity i.e. all of the probailities would be the same and it would basically mean picking one out randomly
    # temp -> 0 i.e. the one with highest probability has probability of 1 now
    # temp = 1 i.e. nothing changes here
    # Higher the values of temp, more predictble would be the sampling

    predictions = np.log(probability_distribution) / temp
    # Applying softmax function for having a more homogenous distribution
    probability_distribution = np.exp(predictions) / np.sum(np.exp(predictions))

    # Sampling out a value from the remodelled distribution
    choices = range(len(probability_distribution))
    index = np.random.choice(choices, p=probability_distribution)

    return index

