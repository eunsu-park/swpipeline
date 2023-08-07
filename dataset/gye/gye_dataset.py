# -*- coding: utf-8 -*-
"""
gye_dataset_log.py
"""
from gye_database import BaseDataset
import numpy as np
import matplotlib.pyplot as plt
# 파일 이름 선언해주기 / 파일이 너무 많을 때 메모리에서 지우는게 필요할까?
class gyeDataset(BaseDataset):
    def __init__(self, file_):
        super(gyeDataset, self).__init__(file_)
        self.file_name = file_
        
    def parsing(self):
        with open(self.file_, 'r') as file:
            d = []
            count = 0
            for line in file:
                data = line.strip().split('\t')
                d = d+data
                
                count += 1
                if count == 100000:
                    break
                
            columns = list(zip(*[line.split() for line in d]))
            column = np.array(columns)
            
            dic = {f'column{i+1}': column for i,column in enumerate(column)}
                            
            HEADER = list(dic.keys())
            DATA = list(dic.values())
            ITEM = list(dic.items())
            
        self.parsing_header(HEADER)
        self.parsing_data(DATA)
        self.parsing_all(ITEM)
        
    def parsing_header(self, HEADER):
        header = np.array(HEADER)
        self.header = header
         
    def parsing_data(self, DATA):
        data = np.array(DATA)
        self.data = data
        
    def parsing_all(self, ITEM):
        self.item = ITEM
        
        all = {'HEADER' : self.header,
               'DATA' : self.data }
        
        self.all = all

class GYEDataset(gyeDataset):
    def __init__(self, file_):
        super(GYEDataset, self).__init__(file_)
        
    def plot(self):
        for i in range(len(self.item)):
            plt.figure(figsize=(9,6))
            c_lst = ['b','c','g','r']
            color_lst = c_lst*4
            plt.plot(self.item[i][1], label = self.header[i], color = color_lst[i])
            
            desired_y_ticks = 6

            y_min, y_max = plt.ylim()
            num_y_ticks = min(desired_y_ticks, int(y_max - y_min) + 1)
            
            y_ticks = np.linspace(y_min, y_max, num_y_ticks)
            plt.yticks(y_ticks,['%.2f' % tick for tick in y_ticks])
            
            plt.title(f'{self.file_name}')
            plt.legend(loc = 'upper left', fontsize = 12)