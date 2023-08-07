import sys
import os
sys.path.append('c:/Users/hws41/KASI/dataset')
from api.ecallisto_dataset import *

file_list = [
    './e_callisto/ec_sp_20190422_040000_59.fit',
    './e_callisto/LPTCS_20090422.log',
    './e_callisto/LPTCS_20190422.txt'
]

n = 0
f = file_list[n]

class_list = [
    EcallistoSpFitDataset(f),
    EcallistoLPTCSLogDataset(f),
    EcallistoLPTCSTxtDataset(f)
]

ecallisto_dataset = class_list[n]
ecallisto_dataset.parsing()
data = ecallisto_dataset.data
print(data)
# print(ecallisto_dataset.header)
# print(ecallisto_dataset.data)
# print(ecallisto_dataset.all)
# ecallisto_dataset.plot()