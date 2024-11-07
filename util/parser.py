import json
import pandas as pd
from random import choice


class JSONParser:
    def __init__(self):
        self.text = []
        self.intents = []
        self.responses = {}

    def parse(self, json_path):
        with open(json_path) as data_file:
            self.data = json.load(data_file)

        for intent in self.data['intents']:

            if 'subintents' in intent:
                for subintent in intent['subintents']:
                    for pattern in subintent['patterns']:
                        self.text.append(pattern)
                        self.intents.append(subintent['tag'])
                    for resp in subintent['responses']:
                        if subintent['tag'] in self.responses:
                            self.responses[subintent['tag']].append(resp)
                        else:
                            self.responses[subintent['tag']] = [resp]
            else:
                for pattern in intent['patterns']:
                    self.text.append(pattern)
                    self.intents.append(intent['tag'])
                for resp in intent['responses']:
                    if intent['tag'] in self.responses:
                        self.responses[intent['tag']].append(resp)
                    else:
                        self.responses[intent['tag']] = [resp]

        # Create DataFrame with updated intents and patterns
        self.df = pd.DataFrame({'text_input': self.text, 'intents': self.intents})

        print(f"[INFO] Data JSON converted to DataFrame with shape : {self.df.shape}")

    def get_dataframe(self):
        return self.df

    def get_response(self, intent):
        return choice(self.responses[intent])
