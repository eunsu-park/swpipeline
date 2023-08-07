from copy import deepcopy
from re import I
from astropy.io import fits
from dataset.lib.header import Header
import numpy as np
from dataset.lib.utilities import *
import warnings
import textwrap
import matplotlib.pyplot as plt
from astropy.visualization import astropy_mpl_style


def aia_fits(filepath):
    return AIAFits(filepath)

def hmi_fits(filepath):
    return HMIFits(filepath)

def sdo_fits(filepath):
    return SDOFits(filepath)

class AIAFits():
    pass

class HMIFits():
    pass

class SDOFits():
    pass

# TODO: verify 'file is AIAFIts'
def aia_fits_open(filepath):
    return AIAFits(filepath)


class AIAFits_():
    """
    Parameters
    ----------
    filepath: str
    """
    def __init__(self, filepath):
        #
        # Change print options of numpy
        np.set_printoptions(precision=25)

        #
        # init variable
        self.header = None
        self.data = None
        self.all = None

        #
        # load file using fits.open()
        all = fits.open(filepath)
        
        #
        # get image extension hdu (for AIA)
        target_hdu = None
        if(len(all) > 2):
            warnings.warn("The number of hdu of SDO AIA is more than two.")

        for hdu in all:
            if(not isinstance(hdu, fits.hdu.image.ImageHDU)):
                continue
            target_hdu = hdu
        
        # ???: 프로그램이 죽어야하나...????
        if(not target_hdu):
            error_msg = "Error in {func_name}():\n\t".format(func_name="__init__")
            error_msg += "There is no image hdu in hduList of SDO AIA"
            raise Exception(error_msg)

        #
        # create header(dict), data(np.ndarray)
        hd = self._convert_header_to_dict(hdu.header)
        header = self._add_info_to_header(hd)
        data = hdu.data

        #
        # set basic member variable
        self.all = all
        self.header = header
        self.data = data
        self._target_hdu = target_hdu
        print(type(target_hdu))
    # @property
    # def size(self):
    #     return np.shape(self.data)

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
        
        #
        # TODO: 조사....
        #      (+) 더 보여주면 좋을 것같은거 추가
        # Scale:\t\t\t {shape}
        # Reference Pixel:\t\t\t {shape}
        # Reference Coord:\t\t\t {shape}

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

    '''
    # NOTE: 보류
    def convert_object_to_datetime(self, obj):
        """
        Parameters
        ----------
        obj: str
        
        Returns
        -------
        result: datetime.datetime
        """
        result = None
        if(isinstance(obj, str)):
            try:
                result = parse(obj)
            except:
                try:
                    result = datetime.strptime(obj, "%Y.%m.%d_%H:%M:%S_TAI")
                except:
                    result = None
        return result
    '''

    def plot(self, plot_setting = {}):
        default_plot_setting = {"cmap": "gray",
                                "log_scale": True,
                                "astropy_mpl_style": True
                                }
        
        
        _plot_setting = deepcopy(plot_setting)
        if(plot_setting == {}):
            _plot_setting = default_plot_setting
        
        image = self.data
        if(_plot_setting["log_scale"]):
            raw_img = image
            raw_min = np.min(raw_img)
            raw_max = np.max(raw_img)
            raw_span = raw_max - raw_min
            raw_y, raw_x = np.histogram(raw_img, bins=np.arange(raw_min, raw_max, raw_span/256))
            scale_img = np.clip(raw_img, 1.0, None)
            scale_img = np.log10(scale_img)
            scale_min = np.min(scale_img)
            scale_max = np.max(scale_img)
            scale_span = scale_max - scale_min
            scale_y, scale_x = np.histogram(scale_img, bins=np.arange(scale_min, scale_max, scale_span/256))
            image = scale_img

        plt.figure()
        
        if(_plot_setting["astropy_mpl_style"]):
            from astropy.visualization import astropy_mpl_style
            plt.style.use(astropy_mpl_style)

        plt.imshow(image,
                cmap=_plot_setting["cmap"],
                )
        plt.colorbar()
        plt.show()