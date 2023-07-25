from dateutil.parser import parse
import numpy as np
from datetime import datetime

class MagnetometerAscii():
    # gm_boh_sec5
    def __init__(self, filepath):
        names = ("Date", "H [nT]", "D [nT]", "Z [nT]", "Proton [nT]")
        formats = ("datetime64[s]", "f8", "f8", "f8", "f8")
        #
        # init variable
        self.header = None
        self.data = None
        self.header_str = None
        self.filepath = filepath

        self._names = names
        self._formats = formats

        #
        # create header, data and header_str
        header_lines, data_lines = self._load_file(filepath)
        hd = {}
        data = self._parsing_data(data_lines, names, formats)        
        header = self._add_info_to_header(hd, data)

        #
        # set basic member variable
        self.header = header
        self.data = data
        self.header_str = header_lines

    @property
    def size(self):
        return np.shape(self.data)
    
    @property
    def columns(self):
        return self.data.dtype.names

    def _add_info_to_header(self, header, data):
        """
        Parameters
        ----------
        header: dict
        data: np.ndarray
        
        Returns
        -------
        header: dict
        """

        #
        # goes common info
        header["Observatory"] = "Bohyun"
        header["Object"] = "Sun"
        header["Src_url"] = ""
        header["Comment"] = ""
        header["History"] = ""
        header["Keycomments"] = {
                                }
        #
        # add info from data
        # NOTE: column명이 바뀌면 에러남 / 무슨 형태로 저장하지? (현재: np.datetime64)
        if("Date" in data.dtype.names):
            header["Obs_start_date"] = data["Date"][0]
            header["Obs_end_date"] = data["Date"][-1]
        return header

    def _load_file(self, filepath):
        """
        Parameters
        ----------
        filepath: str
            filepath to read
        
        Returns
        -------
        header_lines: list
            lines of header
        data_lines: list
            lines of data
        """
        header_lines = []
        data_lines = []

        with open(filepath, "r") as f:
            # NOTE: f.readlines(): contains "\n"
            for i, line in enumerate(f.read().splitlines()):
                if(i == 0):
                    header_lines.append(line)
                    continue
                data_lines.append(line)
        return header_lines, data_lines

    '''
    def _parsing_header(self, header_lines):
        pass
    '''

    def _parsing_data(self, data_lines, names, formats):
        """
        Parameters
        ----------
        data_lines: list
            lines of data
        names: tuple
            data columnes
        formats: tuple
            data type for each data column

        Returns
        -------
        data: list
            data: np.ndarray
        """
        data = []
        date_format = "{0}-{1}-{2}T{3}:{4}:{5}"

        for line in data_lines:
            if(line.strip == ""):
                continue
            
            values = line.split()
            #NOTE: doy??????
            Y, m, d, doy, H, M, S = values.pop(0), values.pop(0), values.pop(0), values.pop(0), values.pop(0), values.pop(0), values.pop(0) 
            date = date_format.format(Y, m, d, H, M, S)

            data_tuple = (date,)
            for value in values:
                data_tuple += (value,)
            data.append(data_tuple)
        data = np.array(data, dtype={'names':names, 'formats':formats})

        return data
    
    '''
    # NOTE: 보류
    def convert_object_to_datetime(self, obj):
        pass
    '''

    def plot(self):
        pass