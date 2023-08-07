# -*- coding: utf-8 -*-
"""
2023 - 07 - 10
sdo_dataset.py (참고용 받아쓰기)
"""
from base_dataset import BaseDataset
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt

def sdo_open(file_):
    hdu=fits.open(file_)[-1]
    if hdu.header["content"] == "Magnetogram":
        dataset = HMIDatasetMagnetogram(file_)
    elif hdu.header["content"] == "Continuum":
        dataset = HMIDatasetContinuum(file_)
    elif hdu.header["content"] == "Dopplergram":
        dataset = HMIDatasetDopplergram(file_)
    else:
        raise NameError("Unknown content")
    return dataset

class SDODataset(BaseDataset):
    def __init__(self, file_):
        super(SDODataset, self).__init__(file_)
        
    def parsing(self):
        self.parsing_header()
        self.parsing_data()
        self.parsing_all()
        
    def parsing_header(self):
        hdu = fits.open(self.file_)[-1]
        header = hdu.header
        self.header = header
        
    def parsing_data(self):
        hdu = fits.open(self.file_)[-1]
        data = hdu.data
        self.data = data
        
    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

class AIADataset(SDODataset):
    def __init__(self, file_):
        super(AIADataset, self).__init__(file_)

    def plot(self):
        pass


class HMIDataset(SDODataset):
    def __init__(self, file_):
        super(HMIDataset, self).__init__(file_)
    
    def plot(self):
        data = self.data
        content = self.header['CONTENT']
        naxis1 = self.header["NAXIS1"]
        cdelt1 = self.header["CDELT1"]
        naxis2 = self.header["NAXIS2"]
        cdelt2 = self.header["CDELT2"]

        xmin = - naxis1 / 2. * cdelt1
        xmax = naxis1 / 2. * cdelt1
        ymin = - naxis2 / 2. * cdelt2
        ymax = naxis2 / 2. * cdelt2
        if content == 'CONTINUUM INTENSITY' :
            vmin, vmax = 0, 65535
        elif content == 'MAGNETOGRAM' :
            vmin, vmax = -100, 100
        elif content == 'DOPPLERGRAM' :
            vmin, vmax = -10000, 10000
        data[np.isnan(data)] = vmin

        plt.figure()
        plt.imshow(data, vmin=vmin, vmax=vmax, extent = [xmin, xmax, ymin, ymax], cmap="gray")
        plt.title("%s %s %s" % (self.header["TELESCOP"], self.header["CONTENT"], self.header["T_REC"]))
        plt.xlabel(self.header["CUNIT1"])
        plt.ylabel(self.header["CUNIT2"])
        plt.colorbar(label=self.header["BUNIT"])
        plt.show()

class HMIMagnetogramDataset(HMIDataset):
    def __init__(self, file_):
        super(HMIMagnetogramDataset, self).__init__(file_)

    def process(self):
        pass