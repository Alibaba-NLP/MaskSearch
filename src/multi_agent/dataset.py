import argparse
import json
import pandas as pd


class BaseDataset:
    def __init__(self):
        self.data = []
    
    def __iter__(self):
        return iter(self.data)
        
    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        return self.data[index]



class HotpotDataset(BaseDataset):
    def __init__(self):
        self.data_path = ""
        self.data = self.load_data()  

    def load_data(self):
        data = []

        with open(self.data_path,'r') as f:
            json_data = json.load(f)
        
            for item in json_data:
                query = item['question']
                answer = item['answer']
                
                data.append({
                    'query': query,
                    'answer': answer,
                    'ext':{
                            'golden_answer' : answer,
                        }
                })
        
        return data
    

