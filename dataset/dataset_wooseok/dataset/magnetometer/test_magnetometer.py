import sys
import os
sys.path.append('c:/Users/hws41/KASI/dataset')
from api.magnetometer_dataset import *

file_list = [
    './magnetometer/gm_boh_min_20220705.txt',
    './magnetometer/gm_boh_sec5_20230710.txt',
    './magnetometer/kindex_201501.txt',
    './magnetometer/mi_boh_mil_20180711.txt',
    './magnetometer/mi_spectrum_20100311_x.txt',
    './magnetometer/mi_spectrum_20100311_y.txt',
    './magnetometer/mi_spectrum_20100311_z.txt',
    './magnetometer/min_average_202007.txt',
    './magnetometer/pi2_list_20100606.dat',
    './magnetometer/pi2_power_20100311.dat'
]

n = 0
f = file_list[n]

class_list = [
    MagnetometerBOHminDataset(f),
    MagnetometerBOHsec5Dataset(f),
    MagnetometerKindexDataset(f),
    MagnetometerBOHmilDataset(f),
    MagnetometerMISpectrumXDataset(f),
    MagnetometerMISpectrumYDataset(f),
    MagnetometerMISpectrumZDataset(f),
    MagnetometerMinAverageDataset(f),
    MagnetometerPi2listDataset(f),
    MagnetometerPi2powerDataset(f)
]

magnetometer_dataset = class_list[n]
magnetometer_dataset.parsing()
print(magnetometer_dataset.header)
print(magnetometer_dataset.data)
print(magnetometer_dataset.all)
magnetometer_dataset.plot()