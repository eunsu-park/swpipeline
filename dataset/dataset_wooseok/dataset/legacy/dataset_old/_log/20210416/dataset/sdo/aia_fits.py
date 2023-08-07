from astropy.io import fits
import numpy as np
from datetime import datetime
from dateutil.parser import parse


class AIAFits():
    def __init__(self, filepath):
        self.hdu_list = None
        self.header = None
        self.data = None
        self.filepath = filepath

        #
        # load file using fits.open()
        hdu_list = fits.open(filepath)
        
        #
        # get image extension hdu (for AIA)
        target_hdu = None
        if(len(hdu_list) > 2):
            print("Warnning: The number of hdu of SDO AIA is more than two.")

        for hdu in hdu_list:
            if(not isinstance(hdu, fits.hdu.image.ImageHDU)):
                continue
            target_hdu = hdu

        if(not target_hdu):
            print("Fail: There is no image hdu in hduList of SDO AIA")
            return None

        #
        # create header(dict), data
        hd = self.convert_header_to_dict(hdu.header)
        header = self.add_info_to_header(hd)
        data = hdu.data

        #
        # set basic member variable
        self.hdu_list = hdu_list
        self.header = header
        self.data = data
        self._target_hdu = target_hdu
    
    @property
    def size(self):
        return np.shape(self.data)

    @property
    def header_str(self):
        # return self._target_hdu.header.tostring("\n").split("\n")
        return self._target_hdu.header.tostring("\n")

    def convert_header_to_dict(self, hdu_header):
        """
        Parameters
        ----------
        hdu_header: astropy.io.fits.header.Header
        
        Returns
        -------
        header: dict
        """
        header = {}

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

    def add_info_to_header(self, header):
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

    def plot(self):
        pass