from re import I
from astropy.io import fits
from dataset.lib.header import Header
import numpy as np
from dataset.lib.utilities import *
import warnings
import textwrap
import matplotlib.pyplot as plt


def aia_open(filepath):
    return AIAFitsDataset(filepath)

def hmi_open(filepath):
    return HMIFitsDataset(filepath)


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


class SDOFitsDataset():
    def __init__(self, filepath):
        # Change print options of numpy
        np.set_printoptions(precision=25)

        # init variable
        self.header = None
        self.data = None
        self.all = None

        # load file using fits.open()
        all = fits.open(filepath)

        # get image extension hdu
        target_hdu = None
        if(len(all) > 2):
            warnings.warn("The number of hdu of SDO AIA is more than two.")

        for hdu in all:
            if(isinstance(hdu, fits.hdu.image.ImageHDU)):
                target_hdu = hdu
            elif(isinstance(hdu, fits.hdu.compressed.CompImageHDU)):
                target_hdu = hdu
            else :
                continue
            target_hdu = hdu

        # ???: 프로그램이 죽어야하나...????
        if(not target_hdu):
            error_msg = "Error in {func_name}():\n\t".format(func_name="__init__")
            error_msg += "There is no image hdu in hduList of SDO"
            raise Exception(error_msg)

        # create header(dict), data(np.ndarray)
        hd = self._convert_header_to_dict(target_hdu.header)
        header = self._add_info_to_header(hd)
        data = target_hdu.data

        # set basic member variable
        self.all = all
        self.header = header
        self.data = data
        self._target_hdu = target_hdu
        print(type(target_hdu))


    def _convert_header_to_dict(self, hdu_header):
        """
        Parameters
        ----------
        hdu_header: astropy.io.fits.header.Header
        
        Returns
        -------
        header: dict
        """
        check_value_type(hdu_header, fits.header.Header, "convert_header_to_dict")
        
        header = Header()
        # header = {}

        keycomments = {}
        for card in hdu_header.cards:
            # NOTE: verify에 문제가 생기면 .value 호출 시 에러가 뜸.
            #       verify("fix") 먼저 호출하면 warn 메세지가 뜸.
            card.verify("fix") 

            key = card.keyword
            comment = card.comment
            value = card.value
            
            if(key == ""):
                continue
            
            header[key] = value
            if(comment != ""):
                keycomments[key] = comment
        header["KEYCOMMENTS"] = keycomments

        return header

    def _add_info_to_header(self, header):
        """
        Parameters
        ----------
        header: dict
        
        Returns
        -------
        header: dict
        """
        check_value_type(header, dict, "add_info_to_header")

        # from header info
        header["OBSERVATORY"] = header["TELESCOP"].split("/")[0]

        # goes common info
        header["OBJECT"] = "Sun"
        header["SRC_URL"] = ""
        
        # NOTE: fits에 존재하는 key라 없더라도 건들지 않는 편이 좋은 것같음
        # header["COMMENT"] = ""
        # header["HISTORY"] = ""
        
        keycomments = {
                        }
        header["KEYCOMMENTS"] = dict(header["KEYCOMMENTS"], **keycomments)
        
        return header

    def __repr__(self):
        rep = textwrap.dedent("""\
            {obj_type}
            -----------------------------------
            header:\t\t dict
            data:\t\t np.ndarray
            all:\t astropy.io.fits.hdu.hdulist.HDUList
            """).format(obj_type=type(self))
        return rep
    
    def info(self):
        header = self.header
        data = self.data

        check_value_type(header, Header, "info")
        check_value_type(data, np.ndarray, "info")

        info = textwrap.dedent("""\
            Observation Date:\t {obs_date}
            Observatory:\t\t {observatory}
            Instrument:\t\t {instrument}
            Wavelength:\t\t {wavelen}
            Exposure Time:\t\t {exptime}
            Dimension:\t\t {shape}
            Data num:\t\t {data_num}
            Object:\t\t\t {object}
            Source:\t\t\t {src}
            {data}\
            """).format(obs_date=header["DATE-OBS"],
                        observatory=header["TELESCOP"],
                        instrument= header["INSTRUME"],
                        wavelen="{} {}".format(header["WAVELNTH"], header["WAVEUNIT"]),
                        exptime="{} s".format(header["EXPTIME"]),
                        shape=data.shape,
                        data_num=data.size,
                        object=header["OBJECT"],
                        src=header["SRC_URL"],
                        data=data
                        )
        print(info)
        

    def prep(self):
        pass

        # CDELT1 = header['CDELT1']
        # CDELT2 = header['CDELT2']
        # CRPIX1 = header['CRPIX1']
        # CRPIX2 = header['CRPIX2']
        # NAXIS1 = header['NAXIS1']
        # NAXIS2 = header['NAXIS2']
        # CROTA2 = header['CROTA2']

        # CRPIX1_new = header['NAXIS1']//2 - 0.5
        # CRPIX2_new = header['NAXIS2']//2 - 0.5
        # CDELT1_new = 0.6
        # CDELT2_new = 0.6

        # header, data = centering_sdo(header, data)
        # header, data = rotating_sdo(header, data)
        

        # header['CRPIX1'] = CRPIX1_new
        # header['CRPIX2'] = CRPIX2_new
        # header['CDELT1'] = CDELT1_new
        # header['CDELT2'] = CDELT2_new

        # self.header.update({
        # 'R_SUN' : self.header['RSUN_OBS']/self.header['CDELT1'],
        # 'LVL_NUM' : 1.5,
        # 'BITPIX' : -64
        # })

    def rotating(self):
        pass

    def centering(self):
        pass

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


class AIAFitsDataset(SDOFitsDataset):
    def __init__(self, filepath):
        super(AIAFitsDataset, self).__init__(filepath)
#        self.normalize()

    def normalize(self):
        exptime = self.header["EXPTIME"]
        data = self.data
        data = data / exptime
        self.header["EXPTIME"] = 1.0
        self.data = data

    def plot(self, vmin=None, vmax=None):

        naxis1 = self.header["NAXIS1"]
        cdelt1 = self.header["CDELT1"]
        naxis2 = self.header["NAXIS2"]
        cdelt2 = self.header["CDELT2"]

        xmin = - naxis1 / 2. * cdelt1
        xmax = naxis1 / 2. * cdelt1
        ymin = - naxis2 / 2. * cdelt2
        ymax = naxis2 / 2. * cdelt2

        wavelnth = self.header['WAVELNTH']
        data = self.data / self.header["EXPTIME"]
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
        self.data_bytescale = bytescale(data)

        plt.figure()
        plt.imshow(data, extent = [xmin, xmax, ymin, ymax], cmap="gray")
        plt.title("%s %s %s" % (self.header["TELESCOP"], self.header["WAVELNTH"], self.header["T_REC"]))
        plt.xlabel(self.header["CUNIT1"])
        plt.ylabel(self.header["CUNIT2"])        
        plt.colorbar(label="DN/sec")
        plt.show()


class HMIFitsDataset(SDOFitsDataset):
    def __init__(self, filepath):
        super(HMIFitsDataset, self).__init__(filepath)

    def plot(self, vmin=None, vmax=None):
        content = self.header['CONTENT']
        naxis1 = self.header["NAXIS1"]
        cdelt1 = self.header["CDELT1"]
        naxis2 = self.header["NAXIS2"]
        cdelt2 = self.header["CDELT2"]

        xmin = - naxis1 / 2. * cdelt1
        xmax = naxis1 / 2. * cdelt1
        ymin = - naxis2 / 2. * cdelt2
        ymax = naxis2 / 2. * cdelt2

        data = self.data
        if (vmin == None) and (vmax == None) :
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