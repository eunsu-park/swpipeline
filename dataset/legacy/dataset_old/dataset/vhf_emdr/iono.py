from dataset.vhf_emdr.all import All
import textwrap
import numpy as np
from dataset.lib.utilities import *
from dataset.lib.header import Header
from collections import namedtuple

# TODO: verify 'file is AIAFIts'
def iono_open(filepath):
    return Iono(filepath)

class Iono:
    def __init__(self, filepath):
        #
        # Change print options of numpy
        # np.set_printoptions(precision=25, threshold=20)
        np.set_printoptions(precision=4, threshold=20)
        
        #
        # Init variables.
        self._pri_magic_num = "20000000"
        self._param_magic_num = "20a00000"
        self._analysed_data_magic_num = "20a10000"
        # All headers have 4 kinds of information.
        self._hdr_len = 4
        # header info index of parameter, analysed data
        self._len_info_idx = 1 # record len
        self._offset_info_idx = 3 # record start offset
        # Data sizes are given as 8-bit bytes, and all data types are integer multiples of 4 bytes.
        self._data_size = 8

        #
        # create idbs_hdu_list, header(dict), data(np.ndarray)
        hex_list = self._load(filepath)
        primary_header, sets = self._parsing_hex(hex_list)
        
        header = self._header(primary_header)
        header = self._add_info_to_header(header)
        data = self._data(sets)
        all = All(primary_header, sets)
        #
        # set basic member variable
        self.header = header
        self.data = data
        self.all = all


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
        hex_list: list
            Hex format file contents enclosed by data size.
        """
        hex_list = ""
        
        #
        # read binary file in hex
        with open(filepath, "rb") as f:
            hex_list = f.read().hex()
        
        #
        # grouping with data size
        hex_list = [hex_list[i:i+self._data_size] for i in range(0, int(len(hex_list)), self._data_size)]
        return hex_list


    def _parsing_hex(self, hex_list):
        """
        Parameters
        ----------
        hex_list: list
            Hex format file contents enclosed by data size.
        
        Returns
        -------
        primary_header: list
        sets: list
        """
        pri_magic_num = self._pri_magic_num
        param_magic_num = self._param_magic_num
        analysed_data_magic_num = self._analysed_data_magic_num
        hdr_len = self._hdr_len
        len_info_idx = self._len_info_idx
        offset_info_idx = self._offset_info_idx
        data_size = self._data_size
        
        primary_header = None
        sets = []

        Set = namedtuple("Set", "parameter, analysed_data")
        Parameter = namedtuple("Parameter", "header, record")
        AnalysedData = namedtuple("AnalysedData", "header, records")
        # idbs_hdu_list = []
        
        #
        # get primary header
        if(hex_list[0] != pri_magic_num):
            print("file format error")
            return None
        pri_hdr_hex_list = hex_list[:hdr_len]
        primary_header = self._parsing_primary_header_hex(pri_hdr_hex_list)
        
        #
        # get header and record of parameter and analysed data
        s_offset = hdr_len
        while(s_offset < len(hex_list)):
            #
            # paramter
            if(hex_list[s_offset] != param_magic_num):
                print("file format error")
                return None
            
            # TODO: 예외처리
            param_hdr_hex_list = hex_list[s_offset:s_offset+hdr_len]
            param_record_len = int(hex_to_int(hex_list[s_offset+len_info_idx])/(data_size/2))
            param_record_offset = int(hex_to_int(hex_list[s_offset+offset_info_idx])/(data_size/2))
            param_record_hex_list = hex_list[param_record_offset:(param_record_offset+param_record_len)]

            param_hdr = self._parsing_parameter_header(param_hdr_hex_list)
            param_record = self._parsing_parameter_record(param_record_hex_list)
            parameter = Parameter(param_hdr, param_record)

            s_offset = param_record_offset+param_record_len

            #
            # analysed data
            if(hex_list[s_offset] != analysed_data_magic_num):
                print("data is not exist")
                if(hex_list[s_offset] == param_magic_num):
                    set_ = Set(parameter, )
                    sets.append(set_)
                    continue
                else:
                    print("file format error")
                    return None
            
            # TODO: 예외처리
            data_hdr_hex_list = hex_list[s_offset:s_offset+hdr_len]
            data_record_len = int(hex_to_int(hex_list[s_offset+len_info_idx])/(data_size/2))
            data_record_offset = int(hex_to_int(hex_list[s_offset+offset_info_idx])/(data_size/2))
            data_record_hex_list = hex_list[data_record_offset:(data_record_offset+data_record_len)]
            
            
            analysed_data_hdr = self._parsing_analysed_data_header(data_hdr_hex_list)
            analysed_data_records = self._parsing_analysed_data_record(data_record_hex_list)
            analysed_data = AnalysedData(analysed_data_hdr, analysed_data_records)

            s_offset = data_record_offset+data_record_len

            set_ = Set(parameter, analysed_data)
            sets.append(set_)
        return primary_header, sets
    

    def _header(self, primary_header):
        """
        Parameters
        ----------
        primary_header: dict
        
        Returns
        -------
        header: Header
        """
        # import copy
        # IdbsPrimaryHDU
        # header = copy.deepcopy(primary_header)
        # del header["magic_num"]
        header = Header()
        for key, value in primary_header.items():
            if(key == "magic_num"):
                continue
            header[key] = value
        return header


    # ???: list는 어떻게 해야하지 이것도 풀어서 써야하나?
    #      - channel은 계속 바뀔 수 있음
    #     데이터가 없다면? -99999?
    def _data(self, sets):
        """
        Parameters
        ----------
        sets: list
        
        Returns
        -------
        data: np.ndarray
            Structured array of parameter and analysed data record.
            Record values ​​are converted values from hex ​​according to each data format.
            The parameter record and analysed data record are one-to-many.
        """
        names = ("time", "range", "error_code", "effective_beam_azimuth", "effective_beam_zenith", "radial_velocity", "spectral_width", "snr", "power")
        formats = ("datetime64[s]", "f8", "i4", "f8", "f8", "f8", "f8", "f8", "f8")
        
        #
        # Create data tuple list.
        # ???: parameter는 있는데 analysed data가 없을 경우 포함시키지 말고 pass??
        data_tuples = []
        for set_ in sets:
            analysed_data = getattr(set_, "analysed_data")    
            AD_header, AD_records = analysed_data
        
            time = AD_header["time"]

            for AD_record in AD_records:
                data_tuple = (time,)
                data_tuple += (AD_record["range"],
                            AD_record["error_code"],
                            AD_record["effective_beam_direction"][0],
                            AD_record["effective_beam_direction"][1],
                            AD_record["radial_velocity"],
                            AD_record["spectral_width"],
                            AD_record["snr"],
                            AD_record["power"],)
                
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

    def _parsing_primary_header_hex(self, header_hex_list):
        """
        Parameters
        ----------
        header_hex_list: list
            Hex format header contents enclosed by data size.
        
        Returns
        -------
        header: dict
        """
        #
        # create header dict
        header = {}
        header["magic_num"] = header_hex_list[0]
        header["num_of_record"] = header_hex_list[1]
        header["start_date"] = header_hex_list[2]
        header["end_date"] = header_hex_list[3]

        #
        # convert hex to data unit
        header["num_of_record"] = hex_to_int(header["num_of_record"])
        header["start_date"] = str(timestamp_to_datetime64(hex_to_int(header["start_date"])))
        header["end_date"] = str(timestamp_to_datetime64(hex_to_int(header["end_date"])))

        return header
    
    def _parsing_parameter_header(self, header_hex_list):
        """
        Parameters
        ----------
        header_hex_list: list
            Hex format header contents of parameter enclosed by data size.
        
        Returns
        -------
        header: dict
        """
        #
        # create header dict
        header = {}
        header["magic_num"] = header_hex_list[0]
        header["length"] = header_hex_list[1]
        header["time"] = header_hex_list[2]
        header["offset"] = header_hex_list[3]

        #
        # convert hex to data unit
        header["length"] = hex_to_int(header["length"])
        header["time"] = str(timestamp_to_datetime64(hex_to_int(header["time"])))
        header["offset"] = hex_to_int(header["offset"])
        
        return header

    def _parsing_parameter_record(self, record_hex_list):
        """
        Parameters
        ----------
        record_hex_list: list
            Hex format record contents of parameter enclosed by data size.
        
        Returns
        -------
        record: dict
        """
        #
        # create record dict
        record = {}
        record["num_of_range"] = record_hex_list[0]
        record["radar_freq"] = record_hex_list[1]
        record["transmit_beam_direction"] = [record_hex_list[2], record_hex_list[3]]
        record["nyquist_velocity"] = record_hex_list[4]
        record["gps_locked"] = record_hex_list[5]
        record["num_of_receiving_channels"] = record_hex_list[6]
        
        channels = []
        num_channels = hex_to_int(record_hex_list[6])
        for i in range(num_channels):
            channels.append(record_hex_list[7+i])
        record["receiving_channels"] = channels
        
        #
        # convert hex to data unit
        record["num_of_range"] = hex_to_int(record["num_of_range"])
        record["radar_freq"] = hex_to_float(record["radar_freq"])
        record["transmit_beam_direction"] = [hex_to_int(x) for x in record["transmit_beam_direction"]]
        record["nyquist_velocity"] = hex_to_float(record["nyquist_velocity"])
        record["gps_locked"] = hex_to_int(record["gps_locked"])
        record["num_of_receiving_channels"] = hex_to_int(record["num_of_receiving_channels"])
        record["receiving_channels"] = [hex_to_int(x) for x in record["receiving_channels"]]
        return record

    def _parsing_analysed_data_header(self, header_hex_list):
        """
        Parameters
        ----------
        header_hex_list: list
            Hex format header contents enclosed by data size.
        
        Returns
        -------
        header: dict
        """
        #
        # create header dict
        header = {}
        header["magic_num"] = header_hex_list[0]
        header["length"] = header_hex_list[1]
        header["time"] = header_hex_list[2]
        header["offset"] = header_hex_list[3]

        #
        # convert hex to data unit
        header["length"] = hex_to_int(header["length"])
        header["time"] = str(timestamp_to_datetime64(hex_to_int(header["time"])))
        header["offset"] = hex_to_int(header["offset"])
        return header

    def _parsing_analysed_data_record(self, record_hex_list):
        """
        Parameters
        ----------
        record_hex_list: list
            Hex format data contents enclosed by data size.
        
        Returns
        -------
        records: list
            format: [record_dict, record_dict, record_dict ...]
        """
        #
        # create record dict
        records = []
        for i in range(0, len(record_hex_list), 8):
            record = {}
            record["range"] = record_hex_list[i]
            record["error_code"] = record_hex_list[i+1]
            record["effective_beam_direction"] = [record_hex_list[i+2], record_hex_list[i+3]]
            record["radial_velocity"] = record_hex_list[i+4]
            record["spectral_width"] = record_hex_list[i+5]
            record["snr"] = record_hex_list[i+6]
            record["power"] = record_hex_list[i+7]
            records.append(record)
        
        #
        # convert hex to data unit
        for record in records:
            record["range"] = hex_to_float(record["range"])
            record["error_code"] = hex_to_int(record["error_code"])
            record["effective_beam_direction"] = [hex_to_float(x) for x in record["effective_beam_direction"]]
            record["radial_velocity"] = hex_to_float(record["radial_velocity"])
            record["spectral_width"] = hex_to_float(record["spectral_width"])
            record["snr"] = hex_to_float(record["snr"])
            record["power"] = hex_to_float(record["power"])
        return records

    # def _get_parameter_header_and_data(self, param_hex_list):
    #     """
    #     Parameters
    #     ----------
    #     param_hex_list: list
    #         Hex format contents enclosed by data size.
        
    #     Returns
    #     -------
    #     header_hex_list: list
    #         Hex format header contents enclosed by data size.
    #     data_hex_list: list
    #         Hex format data contents enclosed by data size.
    #     """
    #     header_str = param_hex_list[:self._hdr_len]
    #     data_str = param_hex_list[self._hdr_len:]
    #     return header_str, data_str