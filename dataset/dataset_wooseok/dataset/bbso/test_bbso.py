import sys
import os
sys.path.append("c:/Users/hws41/KASI/dataset")
from api.bbso_dataset import *

file_list = [
    './bbso/bbso_halph_fl_20230710_230205.fts',
    './bbso/bbso_halph_fr_20230710_230205.fts',
    './bbso/bbso_logs_20230710.txt',
    './bbso/oact_halph_fl_20110630_072800.fts.gz',
    './bbso/oact_halph_fr_20110630_072800.fts.gz'
]

n = 3
f = file_list[n]

class_list = [
    BBSOFtsDataset(f),
    BBSOFtsDataset(f),
    BBSOTxtDataset(f),
    BBSOFtsDataset(f),
    BBSOFtsDataset(f)
]

bbso_dataset = class_list[n]
bbso_dataset.parsing()
print(bbso_dataset.header)
print(bbso_dataset.data)
print(bbso_dataset.all)
bbso_dataset.plot()