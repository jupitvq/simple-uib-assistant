import json
import pandas as pd
from random import choice

class JSONParser:
    def __init__(self):
        self.text = []
        self.intents = []
        self.responses = {}

    def parse(self, json_path):
        with open(json_path, encoding='utf-8') as data_file:
            self.data = json.load(data_file)

        for intent in self.data['intents']:
            if 'subintents' in intent:
                for subintent in intent['subintents']:
                    if 'patterns' in subintent:
                        for pattern in subintent['patterns']:
                            self.text.append(pattern)
                            self.intents.append(subintent['tag'])
                    else:
                        print(f"[ERROR] Tidak ada 'patterns' di intent: {subintent}")
                    
                    if 'responses' in subintent:
                        for resp in subintent['responses']:
                            if subintent['tag'] in self.responses:
                                self.responses[subintent['tag']].append(resp)
                            else:
                                self.responses[subintent['tag']] = [resp]
                    else:
                        print(f"[ERROR] Tidak ada 'responses' di subintent: {subintent}")
            else:
                if 'patterns' in intent:
                    for pattern in intent['patterns']:
                        self.text.append(pattern)
                        self.intents.append(intent['tag'])
                else:
                    print(f"[ERROR] Tidak ada 'patterns' di intent: {intent}")
                
                if 'responses' in intent:
                    for resp in intent['responses']:
                        if intent['tag'] in self.responses:
                            self.responses[intent['tag']].append(resp)
                        else:
                            self.responses[intent['tag']] = [resp]
                else:
                    print(f"[ERROR] Tidak ada 'responses' di intent: {intent}")

        self.df = pd.DataFrame({'text_input': self.text, 'intents': self.intents})

        print(f"[INFO] Data JSON diubah ke DataFrame dengan bentuk : {self.df.shape}")

    def get_dataframe(self):
        return self.df

    def get_response(self, intent):
        return choice(self.responses[intent])