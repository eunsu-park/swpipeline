import sys
import os
sys.path.append("c:/Users/hws41/KASI/dataset")
from api.bbso_dataset import BBSOFtsDataset
from api.bbso_dataset import BBSOTxtDataset
import gzip
import numpy as np
import struct
from astropy.io import fits

f1 = "./bbso/oact_halph_fl_20110630_072800.fts.gz"
f2 = "./bbso/oact_halph_fr_20110630_072800.fts.gz"

with gzip.open(f1, 'r') as file:
    content = file.read()
print(content)
print(fits.open(f1))
hdu = fits.open(f1)
print(hdu[0].data)
# float_array = np.array(struct.unpack('f' * (len(content) // 4), content))
# print(float_array)
# print(float_array.shape)