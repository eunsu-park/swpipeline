# -*- coding: utf-8 -*-
"""
gye_graph.py
"""
from gye_dataset import GYEDataset

f1 = "channel.log"
f2 = "iono.log"
f3 = "navsol.log"
f4 = "scint.log"
f5 = "txinfo.log"

fs = [f1, f2, f3, f4, f5]

for f in fs :
    gye_dataset=GYEDataset(f)
    gye_dataset.parsing()
    gye_dataset.plot()
    print(gye_dataset.header)
    print(gye_dataset.data)
    print(gye_dataset.all)
