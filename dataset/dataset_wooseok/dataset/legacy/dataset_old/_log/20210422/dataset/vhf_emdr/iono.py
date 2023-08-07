import textwrap
from dataset.vhf_emdr.idbs_hdu import *
import numpy as np
from dataset.lib.utilities import *

# TODO: verify 'file is AIAFIts'
def iono_open(filepath):
    return Iono(filepath)

class Iono:
    def __init__(self, filepath):
        #
        # Init variables.
        self._pri_hdr_magic_num = "20000000"
        self._param_hdr_magic_num = "20a00000"
        self._data_hdr_magic_num = "20a10000"
        # All headers have 4 kinds of information.
        self._hdr_len = 4
        # header info index of parameter, analysed data
        self._len_info_idx = 1 # record len
        self._offset_info_idx = 3 # record start offset
        # Data sizes are given as 8-bit bytes, and all data types are integer multiples of 4 bytes.
        self._data_size = 8

        #
        # create idbs_hdu_list, header(dict), data(np.ndarray)
        hex_str = self._load(filepath)
        idbs_hdu_list = self._parsing_hex(hex_str)
        header = self._parsing_header(idbs_hdu_list)
        header = self._add_info_to_header(header)
        data = self._parsing_data(idbs_hdu_list)
        
        #
        # set basic member variable
        self.idbs_hdu_list = idbs_hdu_list
        self.header = header
        self.data = data

    def __repr__(self):
        rep = textwrap.dedent("""\
            {obj_type}
            -----------------------------------
            idbs_hdu_list:\t IdbsHDU object list
                    \t ([IdbsPrimaryHDU, (IdbsParameterHDU, IdbsAnalysedDataHDU), (IdbsParameterHDU, IdbsAnalysedDataHDU)...])
            header:\t\t dict
            data:\t\t structured array(np.ndarray)\
            """).format(obj_type=type(self))
        return rep
    
    def info(self):
        header = self.header
        data = self.data
    
        fields = data.dtype.names
        data_num = data.size * len(fields)

        info = textwrap.dedent("""\
            Obs start date:\t\t {obs_start_date}
            Obs start date:\t\t {obs_end_date}
            Institute:\t\t {institute}
            Instrument:\t\t {instrument}
            Fields:\t\t\t {fields}
            Dimension:\t\t {shape}
            Data num:\t\t {data_num}
            Object:\t\t\t {object}
            Source:\t\t\t {src}
            {data}\
            """).format(obs_start_date=header["start_date"],
                        obs_end_date=header["end_date"],
                        institute=header["institute"],
                        instrument=header["instrument"],
                        fields=fields,
                        shape=data.shape,
                        data_num=data_num,
                        object=header["object"],
                        src=header["src_url"],
                        data=data
                        )
        print(info)

    def _load(self, filepath):
        """
        Parameters
        ----------
        filepath: str
            filepath to read
        
        Returns
        -------
        hex_str: list
            Hex format file contents enclosed by data size.
        """
        hex_str = ""
        
        #
        # read binary file in hex
        with open(filepath, "rb") as f:
            hex_str = f.read().hex()
        
        #
        # grouping with data size
        hex_str = [hex_str[i:i+self._data_size] for i in range(0, int(len(hex_str)), self._data_size)]
        return hex_str


    def _parsing_hex(self, hex_str):
        """
        Parameters
        ----------
        hex_str: list
            Hex format file contents enclosed by data size.
        
        Returns
        -------
        idbs_hdu_list: list
            list of hdu objects.
            IdbsParameterHDUs and IdbsAnalysedDataHDUs of the same date are enclosed in tuples.
            format: [IdbsPrimaryHDU, (IdbsParameterHDU, IdbsAnalysedDataHDU), (IdbsParameterHDU, IdbsAnalysedDataHDU)...]
        """
        pri_hdr_magic_num = self._pri_hdr_magic_num
        param_hdr_magic_num = self._param_hdr_magic_num
        data_hdr_magic_num = self._data_hdr_magic_num
        hdr_len = self._hdr_len
        len_info_idx = self._len_info_idx
        offset_info_idx = self._offset_info_idx
        data_size = self._data_size
        
        idbs_hdu_list = []
        
        #
        # get primary header
        if(hex_str[0] != pri_hdr_magic_num):
            print("file format error")
            return None
        pri_hdr_str = hex_str[:hdr_len]
        idbs_hdu_list.append(IdbsPrimaryHDU(pri_hdr_str))
        
        #
        # get header and record of parameter and analysed data
        s_offset = hdr_len
        set_ = ()
        while(s_offset < len(hex_str)):
            #
            # paramter
            if(hex_str[s_offset] != param_hdr_magic_num):
                print("file format error")
                return None
            
            # TODO: 예외처리
            param_hdr_str = hex_str[s_offset:s_offset+hdr_len]
            param_record_len = int(hex_to_int(hex_str[s_offset+len_info_idx])/(data_size/2))
            param_record_offset = int(hex_to_int(hex_str[s_offset+offset_info_idx])/(data_size/2))
            param_record_str = hex_str[param_record_offset:(param_record_offset+param_record_len)]

            param_str = param_hdr_str + param_record_str

            s_offset = param_record_offset+param_record_len

            #
            # analysed data
            if(hex_str[s_offset] != data_hdr_magic_num):
                print("data is not exist")
                if(hex_str[s_offset] == param_hdr_magic_num):
                    set_ = (IdbsParameterHDU(param_str),)
                    idbs_hdu_list.append(set_)
                    continue
                else:
                    print("file format error")
                    return None
            
            # TODO: 예외처리
            data_hdr_str = hex_str[s_offset:s_offset+hdr_len]
            data_record_len = int(hex_to_int(hex_str[s_offset+len_info_idx])/(data_size/2))
            data_record_offset = int(hex_to_int(hex_str[s_offset+offset_info_idx])/(data_size/2))
            data_record_str = hex_str[data_record_offset:(data_record_offset+data_record_len)]
            
            data_str = data_hdr_str + data_record_str

            s_offset = data_record_offset+data_record_len

            set_ = (IdbsParameterHDU(param_str), IdbsAnalysedDataHDU(data_str))
            idbs_hdu_list.append(set_)
        return idbs_hdu_list
    

    def _parsing_header(self, idbs_hdu_list):
        """
        Parameters
        ----------
        idbs_hdu_list: list
            list of hdu objects.
            IdbsParameterHDUs and IdbsAnalysedDataHDUs of the same date are enclosed in tuples.
            format: [IdbsPrimaryHDU, (IdbsParameterHDU, IdbsAnalysedDataHDU), (IdbsParameterHDU, IdbsAnalysedDataHDU)...]
        
        Returns
        -------
        header: dict
            Gets the header of the IdbsPrimaryHDU.
            Header values ​​are converted values from hex ​​according to each data format.
        """
        import copy
        # IdbsPrimaryHDU
        idbs_primary_hdu = copy.deepcopy(idbs_hdu_list[0].header)
        return idbs_primary_hdu


    # ???: list는 어떻게 해야하지 이것도 풀어서 써야하나?
    #      - channel은 계속 바뀔 수 있음
    #     데이터가 없다면? -99999?
    def _parsing_data(self, idbs_hdu_list):
        """
        set(same date): (ParamterHDU, IdbsAnalysedDataHDU)

        Parameters
        ----------
        idbs_hdu_list: list
            list of hdu objects.
            IdbsParameterHDUs and IdbsAnalysedDataHDUs of the same date are enclosed in tuples.
            format: [IdbsPrimaryHDU, (IdbsParameterHDU, IdbsAnalysedDataHDU), (IdbsParameterHDU, IdbsAnalysedDataHDU)...]
        
        Returns
        -------
        data: np.ndarray
            Structured array of parameter and analysed data record.
            Record values ​​are converted values from hex ​​according to each data format.
            The parameter record and analysed data record are one-to-many.
        """
        names = ("time", "range", "error_code", "effective_beam_azimuth", "effective_beam_zenith", "radial_velocity", "spectral_width", "snr", "power", "num_of_range", "radar_freq", "transmit_beam_azimuth", "transmit_beam_zenith", "nyquist_velocity", "gps_locked", "num_of_receiving_channels", "receiving_channels")
        formats = ("datetime64[s]", "f8", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "i4", "f8", "i4", "i4", "f8", "i4", "i4", "object")
        
        _idbs_hdu_list = idbs_hdu_list
        #
        # Remove IdbsPrimaryHDU from idbs_hdu_list
        if(isinstance(idbs_hdu_list[0], IdbsPrimaryHDU)):
            _idbs_hdu_list = idbs_hdu_list[1:]
        
        #
        # Create data tuple list.
        data_tuples = []
        
        for param, data in _idbs_hdu_list:
            time = param.header["time"]
            if(time != data.header["time"]):
                print("error: param and data time is not same")
                return None
            
            prm = param.data
            for dt in data.data:
                data_tuple = (time,)
                data_tuple += (dt["range"], dt["error_code"], dt["effective_beam_direction"][0], dt["effective_beam_direction"][1], dt["radial_velocity"], dt["spectral_width"], dt["snr"], dt["power"],)
                data_tuple += (prm["num_of_range"], prm["radar_freq"], prm["transmit_beam_direction"][0], prm["transmit_beam_direction"][1], prm["nyquist_velocity"], prm["gps_locked"], prm["num_of_receiving_channels"], prm["receiving_channels"])
                
                data_tuples.append(data_tuple)
        
        #
        # Create structured array.
        data = np.array(data_tuples, dtype={'names':names, 'formats':formats})
        return data


    def _add_info_to_header(self, header):
        """
        Parameters
        ----------
        header: dict
        
        Returns
        -------
        header: dict
        """

        #
        # add info from header info
 
        #
        # goes common info
        header["institute"] = "Kasi"
        header["instrument"] = "VHF Radar"
        header["object"] = ""
        header["src_url"] = ""
        header["comment"] = ""
        header["history"] = ""
        # header["Keycomments"] = {
        #                         "Location": "Longitude of satellite.",
        #                         }

        return header