import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits


class Dataset:
    def __call__(self):
        return 0

def rescale(data, imin, imax, omin, omax):
    odif = omax-omin
    idif = imax-imin
    data = (data-imin)*(odif/idif) + omin
    return data.clip(omin, omax)

def bytescale(data, imin=None, imax=None):
    if not imin:
        imin = np.min(data)
    if not imax:
        imax = np.max(data)
    data = rescale(data, imin, imax, omin=0, omax=255)
    return data.astype(np.uint8)


def aia_intscale(header, data):
    wavelnth = header['WAVELNTH']
    if wavelnth == 94:
        data = np.sqrt((data*4.99803).clip(1.5, 50.))
    elif wavelnth == 131:
        data = np.log10((data*6.99685).clip(7.0, 1200.))
    elif wavelnth == 171:
        data = np.sqrt((data*4.99803).clip(10., 6000.))
    elif wavelnth == 193:
        data = np.log10((data*2.99950).clip(120., 6000.))
    elif wavelnth == 211:
        data = np.log10((data*4.99801).clip(30., 13000.))
    elif wavelnth == 304:
        data = np.log10((data*4.99941).clip(15., 600.))
    elif wavelnth == 335:
        data = np.log10((data*6.99734).clip(3.5, 1000.))
    elif wavelnth == 1600:
        data = (data*2.99911).clip(0., 1000.)
    elif wavelnth == 1700:
        data = (data*1.00026).clip(0., 2500.)
    elif wavelnth == 4500:
        data = (data*1.00026).clip(0., 26000.)
    return data

def hmi_intscale(header, data):
    if header['CONTENT'] == 'CONTINUUM INTENSITY' :
        data = data.clip(0, 65535)
        data = bytescale(data)
    elif header['CONTENT'] == 'MAGNETOGRAM' :
        data = data.clip(-100, 100)
        data = bytescale(data)
    elif header['CONTENT'] == 'DOPPLERGRAM' :
        data = data.clip(-1000, 1000)
        data = bytescale(data)
    return data

def sdo_intscale(header, data):
    if header['INSTRUME'].lower()[:3] == 'hmi' :
        return hmi_intscale(header, data)
    elif header['INSTRUME'].lower()[:3] == 'aia' :
        return aia_intscale(header, data)
    else :
        assert True



def rotating_sdo(header, data):
    ## scipy? scikit-image?
    return header, data

def centering_sdo(header, data):
    ## is it necessary to apply subpix interpolation?
    return header, data

def normalizing_aia(header, data):
    exptime = header['EXPTIME']
    data = data / exptime
    header['EXPTIME'] = 1.0
    return header, data

def prep_sdo(sdodataset):
    #Centering, Rotating
    header = sdodataset.header
    data = sdodataset.data

    CDELT1 = header['CDELT1']
    CDELT2 = header['CDELT2']
    CRPIX1 = header['CRPIX1']
    CRPIX2 = header['CRPIX2']
    NAXIS1 = header['NAXIS1']
    NAXIS2 = header['NAXIS2']
    CROTA2 = header['CROTA2']

    CRPIX1_new = header['NAXIS1']//2 - 0.5
    CRPIX2_new = header['NAXIS2']//2 - 0.5
    CDELT1_new = 0.6
    CDELT2_new = 0.6

    header, data = centering_sdo(header, data)
    header, data = rotating_sdo(header, data)
    

    header['CRPIX1'] = CRPIX1_new
    header['CRPIX2'] = CRPIX2_new
    header['CDELT1'] = CDELT1_new
    header['CDELT2'] = CDELT2_new

    header.update({
        'R_SUN' : header['RSUN_OBS']/header['CDELT1'],
        'LVL_NUM' : 1.5,
        'BITPIX' : -64
    })

    sdodataset.header = header
    sdodataset.data = data

    return sdodataset


class SDODataset(Dataset):

    def read_fits(self, file_fits):
        hdu = fits.open(file_fits)
        self.all = hdu.copy()
        self.aheader = hdu[1].header
        self.data = hdu[1].data
        hdu.close()

    def header_to_dict(self):
        self.header = dict()
        for key in self.aheader.keys():
            try :
                self.header.update({key:self.aheader[key]})
            except :
                self.header.update({key:np.nan})

    def plot(self):
        image = sdo_intscale(self.header, self.data)
        plt.imshow(image, cmap='gray')
        plt.show()



class HMIDataset(SDODataset):

    def __init__(self, file_fits):
        self.read_fits(file_fits)
        self.header_to_dict()
        self.convert_nan()

    def convert_nan(self):
        w = np.where(np.isnan(self.data))
        self.data[w] = 0.

class AIADataset(SDODataset):

    def __init__(self, file_fits):
        self.read_fits(file_fits)
        self.header_to_dict()


if __name__ == '__main__' :

    from glob import glob
    list_fits = glob('./TestData/*.fits')
    nb_fits = len(list_fits)
    print(nb_fits)

    for file_fits in list_fits :
        if 'aia' in file_fits :
            dataset = AIADataset(file_fits)
        elif 'hmi' in file_fits :
            dataset = HMIDataset(file_fits)
        header = dataset.header
        data = dataset.data
        print(header['WAVELNTH'], data.shape, dataset.all)

    dataset.plot()
    print(dataset.header['CDELT1'])
    prep_sdo(dataset)
    print(dataset.header['CDELT1'])

