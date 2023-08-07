import sys
import os
sys.path.append('c:/Users/hws41/KASI/dataset')
from api.swpc_dataset import *

file_list = [
    './swpc/2022_DSD.txt',
    './swpc/20230713dayobs.txt',
    './swpc/20230713daypre.txt',
    './swpc/20230713RSGA.txt',
    './swpc/20230713SGAS.txt',
    './swpc/20230713SRS.txt',
    './swpc/swpc_aurora_power_20230713.txt'
]

n = 6
f = file_list[n]

class_list = [
    SWPCDSDDataset(f),
    SWPCDayobsDataset(f),
    SWPCDaypreDataset(f),
    SWPCRSGADataset(f),
    SWPCSGASDataset(f),
    SWPCSRSDataset(f),
    SWPCAuroraPowerDataset(f)
]

swpc_dataset = class_list[n]
swpc_dataset.parsing()
print(swpc_dataset.header)
print(swpc_dataset.data)
print(swpc_dataset.all)
swpc_dataset.plot()