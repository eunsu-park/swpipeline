from dateutil.parser import parse
import numpy as np
from datetime import datetime

class DiagnosticRAscii():
    def __init__(self, filepath):
        names = ("Date", "R")
        formats = ("datetime64[s]", "i4")

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
        hd = self._parsing_header(header_lines)
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
        
        Returns
        -------
        header: dict
        """

        """
        #
        # add info from header info
        interval = header["filename"].split(".txt")[0][-2:]
        time_itv, time_unit = int(interval[0]), interval[1]
        if(time_unit == "m"):
            time_itv *= 60
        header["time_interval"] = time_itv
        """

        #
        # goes common info
        header["Observatory"] = "Kasi"
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
        header_delimiters = "------"
        header_lines = []
        data_lines = []
        
        hdr_dlmt_idx = -1
        lines = None
        with open(filepath, "r") as f:
            # NOTE: f.readlines(): contains "\n"
            lines = f.read().splitlines()
            for i, line in enumerate(lines):
                if(header_delimiters in line):
                    hdr_dlmt_idx = i
                    break
        
        if(hdr_dlmt_idx == -1):
            hdr_dlmt_idx = len(lines)

        header_lines = lines[:hdr_dlmt_idx+1]
        data_lines = lines[hdr_dlmt_idx+1:]

        return header_lines, data_lines

    # TODO: Label, Units -> dict형태로 보여주는 것이 좋은지 질문할 것
    def _parsing_header(self, header_lines):
        """
        Parameters
        ----------
        header_lines: list
            lines of header
        
        Returns
        -------
        header: dict
        """

        header = {}

        notes = []
        for i, line in enumerate(header_lines):
            line = line.strip()
            
            # Skip from column to end.
            if(i >= len(header_lines)-2):
                continue

            if(line == ""):
                continue

            # Put anything that is not in the key-value form in 'note'.
            notes.append(line)
        header["Note"] = notes

        return header

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
        date_format = "{0}-{1}-{2}T{3}:{4}"

        for line in data_lines:
            if(line.strip == ""):
                continue
            values = line.split("#")
            Ymd, HM = values.pop(0), values.pop(0)
            Y, m, d, H, M = Ymd[:4], Ymd[4:6], Ymd[6:], HM[:2], HM[2:]
            date = date_format.format(Y, m, d, H, M)

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