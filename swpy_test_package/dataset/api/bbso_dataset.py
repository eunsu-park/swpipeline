from .base_dataset import BaseDataset
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt


class BBSODataset(BaseDataset):
    def __init__(self, file_):
        super(BBSODataset, self).__init__(file_)
    #     self.parsing()

class BBSOFtsDataset(BBSODataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        self.parsing_header()
        self.parsing_data()
        self.parsing_all()

    def parsing_header(self):
        hdu = fits.open(self.file_)[-1]
        header = hdu.header
        self.header = dict(header.items())

    def parsing_data(self):
        hdu = fits.open(self.file_)[-1]
        data = hdu.data
        self.data = data

    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        data = self.data
        naxis1 = self.header["NAXIS1"]
        cdelt1 = self.header["CDELT1"]
        naxis2 = self.header["NAXIS2"]
        cdelt2 = self.header["CDELT2"]

        xmin = - naxis1 / 2. * cdelt1
        xmax = naxis1 / 2. * cdelt1
        ymin = - naxis2 / 2. * cdelt2
        ymax = naxis2 / 2. * cdelt2
        vmin, vmax = np.min(data), np.max(data)

        plt.figure()
        plt.imshow(data, vmin=vmin, vmax=vmax, extent = [xmin, xmax, ymin, ymax], cmap="gray")
        plt.title("%s" % (self.header["COMMENT"]))
        plt.xlabel(self.header["CTYPE1"])
        plt.ylabel(self.header["CTYPE2"])
        plt.show()

class BBSOTxtDataset(BBSODataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None
    
    def parsing(self):
        with open(self.file_, 'r') as file:
            content = file.read()
            pattern = '+------   H-alpha   ------------------------------------------------------------+'
            header, data = content.split(pattern, 1)
            self.parsing_header(header)
            self.parsing_data(pattern, data)
            self.parsing_all()

    def parsing_header(self, header):
        self.header = header.strip()

    def parsing_data(self, pattern, data):
        self.data = pattern + '\n' + data.strip()
            
    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        pass

class BBSOFtsGzDataset(BBSODataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        self.parsing_header()
        self.parsing_data()
        self.parsing_all()

    def parsing_header(self):
        hdu = fits.open(self.file_)[-1]
        header = hdu.header
        self.header = dict(header.items())

    def parsing_data(self):
        hdu = fits.open(self.file_)[-1]
        data = hdu.data
        self.data = data

    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        data = self.data
        naxis1 = self.header["NAXIS1"]
        naxis2 = self.header["NAXIS2"]

        xmin = - naxis1 / 2.
        xmax = naxis1 / 2.
        ymin = - naxis2 / 2.
        ymax = naxis2 / 2.
        vmin, vmax = np.min(data), np.max(data)

        plt.figure()
        plt.imshow(data, vmin=vmin, vmax=vmax, extent = [xmin, xmax, ymin, ymax], cmap="gray")
        plt.title("%s" % (self.header["COMMENT"]))
        plt.show()