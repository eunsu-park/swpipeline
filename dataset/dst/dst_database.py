"""
dataset.py
"""
from abc import ABC, abstractmethod

class BaseDataset(ABC):
    def __init__(self, file_):
        self.file_ = file_
        self.data = None
        self.header = None
        self.all = None
        
    @abstractmethod
    def parsing(self):
        pass
    
    @abstractmethod
    def parsing_header(self):
        pass
    
    @abstractmethod
    def parsing_data(self):
        pass
    
    @abstractmethod
    def parsing_all(self):
        pass
    
    @abstractmethod
    def plot(self):
        pass
