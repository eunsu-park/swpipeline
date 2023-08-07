import sys
import os
sys.path.append('c:/Users/hws41/KASI/dataset')
from api.ace_dataset import *

file_list = [
    './ace/20190422_ace_mag_1m.txt',
    './ace/20190422_ace_sis_5m.txt',
    './ace/20190422_ace_swepam_1m.txt'
]

n = 2
f = file_list[n]

class_list = [
    AceMagDataset(f),
    AceSisDataset(f),
    AceSwepamDataset(f)
]

ace_dataset = class_list[n]
ace_dataset.parsing()
print(ace_dataset.header)
print(ace_dataset.data)
print(ace_dataset.all)
ace_dataset.plot()