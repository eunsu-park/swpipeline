import sys
import os
sys.path.append('c:/Users/hws41/KASI/dataset')
from api.dscovr_dataset import *

file_list = [
    './dscovr/dscovr_mag_20230717.txt',
    './dscovr/dscovr_plasma_20230717.txt'
]

n = 1
f = file_list[n]

class_list = [
    DscovrMagDataset(f),
    DscovrPlasmaDataset(f)
]

dscovr_dataset = class_list[n]
dscovr_dataset.parsing()
print(dscovr_dataset.header)
print(dscovr_dataset.data)
print(dscovr_dataset.all)
dscovr_dataset.plot()