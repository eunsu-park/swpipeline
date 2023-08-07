import sys
import os
sys.path.append("c:/Users/hws41/KASI/dataset")
from api.sdo_dataset import HMIDataset

f1 = "./test/hmi_magnetogram.fits"
f2 = "./test/hmi_continuum.fits"
f3 = "./test/hmi_dopplergram.fits"

# fs = [f1, f2, f3]
print("/\n/\n/\n/\n/\n/\n")
fs = [f3]

for f in fs :
    hmi_dataset = HMIDataset(f)
    hmi_dataset.parsing()
    print(hmi_dataset.all)
    hmi_dataset.plot()