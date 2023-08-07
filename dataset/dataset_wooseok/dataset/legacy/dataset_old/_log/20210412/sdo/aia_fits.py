from astropy.io import fits
import numpy as np
from datetime import datetime
from dateutil.parser import parse


def read(filepath):
    """
    Parameters
    ----------
    filepath: str
        filepath to read
    
    Returns
    -------
    aiafits: AIAfits object
    """
    # parsing file using fits.open()
    hduList = fits.open(filepath)

    # get image extension hdu (for AIA)
    target_hdu = None
    if(len(hduList) > 2):
        print("Warnning: The number of hdu of SDO AIA is more than two.")

    for hdu in hduList:
        if(not isinstance(hdu, fits.hdu.image.ImageHDU)):
            continue
        target_hdu = hdu

    if(not target_hdu):
        print("Fail: There is no image hdu in hduList of SDO AIA")
        return None

    # get header, header_str, data
    # header = hdu.header
    hd, header_str = get_header_info_from_hdu_header(hdu.header)
    header = add_info_to_header(hd)
    data = hdu.data
    
    
    aiafits = AIAFits(header, data, header_str, filepath)
    return aiafits


def get_header_info_from_hdu_header(hdu_header):
    """
    Parameters
    ----------
    hdu_header: astropy.io.fits.header.Header
    
    Returns
    -------
    header: dict
    header_str: list
    """
    header = {}
    header_str = []

    keycomments = {}
    for card in hdu_header.cards:
        line = card.image
        value = card.value # card.image보다 앞에오면 죽음
        key = card.keyword
        comment = card.comment
        
        if(key == ""):
            continue
        
        header[key] = value
        if(comment != ""):
            keycomments[key] = comment
        header_str.append(line)
    header["KEYCOMMENTS"] = keycomments

    return header, header_str

# NOTE: TIME_STD -> 1977.01.01_00:00:00_TAI(International Atomic Time) => not utc
def add_info_to_header(header):
    """
    Parameters
    ----------
    header: dict
    
    Returns
    -------
    header: dict
    """
    # from header info
    header["OBSERVATORY"] = header["TELESCOP"].split("/")[0]

    # goes common info
    header["OBJECT"] = "Sun"
    header["TIME_STD"] = "utc"
    header["SRC_URL"] = ""
    header["COMMENT"] = ""
    header["HISTORY"] = ""
    header["TIME_INTERVAL"] = 1800
    
    keycomments = {
                    "TIME_INTERVAL": "The interval at which data is recorded. Time unit is second."
                    }
    header["KEYCOMMENTS"] = dict(header["KEYCOMMENTS"], **keycomments)
    
    return header



class AIAFits():
    def __init__(self, header, data, header_str, filepath):
        self.header = header
        self.data = data
        self.header_str = header_str
        self.filepath = filepath

    @property
    def size(self):
        return np.shape(self.data)

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


    def plot(self):
        pass