# Each ADF analysed data file begins with a four longword information header made up of [File magic number, Number of ADF records in file, Time stamp of first record in file, Time stamp of last record in file]. The first element (32 bits) is the magic number and revision number. The file magic number is 0x2000xxxx, where xxxx is the revision number of the file as a whole. The number of AADF records refers to the total number of information records (each type of which is detailed below) contained in the entire file.
# Each parameter record is preceded by a four longword information header. The first element is the magic number and revision number for that parameter block. The second element is the length (in bytes) of the parameter block. The third longword is the time at which the parameter block was written (Unix format). The fourth longword is the offset (in bytes) in the file of the beginning of the parameters.
# An analysed data record is stored after its applicable parameter record. Since an analysed data file usually contains more than one data point, a single analysed data file will typically contain multiple sets of parameter and analysed data records.
# All data sizes are given as 8-bit bytes, and all data types are integer multiples of 4 bytes. Multiple-byte integers are written as signed, network order entities.
# Data format revisions are recorded in the magic number system using the least significant 16 bit of the number. Header revision numbers are independent of each other.
# Note that all velocities are specified in terms of the direction in which the wind is heading. All vertical and radial velocities are specified as positive in the direction away from the radar, such that positive vertical velocities are upwards.
# All analysed data records are stored from lowest to highest range.
# => 모든 header 소개: longword information header

from dataset.lib.utilities import *
from abc import *
from dataset.lib.header import Header

class _IdbsHDU(metaclass=ABCMeta):
    """
    Parameters
    ----------
    hex_content_str: list
        Hex format contents enclosed by data size.
    """
    hdr_len = 4

    def __init__(self, hex_content_str):
        pass
        
    @property
    def _hdr_len(cls):
        return cls.hdr_len

    @abstractmethod
    def _get_header_and_data(self, hex_content_str):
        pass
    
    @abstractmethod
    def _parsing_header(self, header_str):
        pass
    
    @abstractmethod
    def _parsing_data(self, data_str):
        pass
    
    @abstractmethod    
    def _convert_header(self, header):
        pass
    
    @abstractmethod
    def _convert_data(self, data):
        pass


class IdbsPrimaryHDU(_IdbsHDU):
    def __init__(self, header_str):
        header_hex = self._parsing_header(header_str)
        header = self._convert_header(header_hex)

        self.header = header
        self.header_str = header_str
    
    def _get_header_and_data(self, hex_content_str):
        pass
    def _parsing_data(self, data_str):
        pass
    def _convert_data(self, data):
        pass

    def _parsing_header(self, header_str):
        """
        Parameters
        ----------
        header_str: list
            Hex format header contents enclosed by data size.
        
        Returns
        -------
        header: dict
            The types of values are hex.
        """
        # header = {}
        header = Header()
        header["magic_num"] = header_str[0]
        header["num_of_record"] = header_str[1]
        header["start_date"] = header_str[2]
        header["end_date"] = header_str[3]
        return header

    def _convert_header(self, header):
        """
        Convert from hex to data ​​according to each data format.

        Parameters
        ----------
        header: dict
            The types of values are hex.
        
        Returns
        -------
        header: dict
            The types of values are data.
        """
        # header["magic_num"] = header["magic_num"]
        header["num_of_record"] = hex_to_int(header["num_of_record"])
        header["start_date"] = str(timestamp_to_datetime64(hex_to_int(header["start_date"])))
        header["end_date"] = str(timestamp_to_datetime64(hex_to_int(header["end_date"])))
        return header

class IdbsParameterHDU(_IdbsHDU):
    def __init__(self, parameter_str):
        header_str, data_str = self._get_header_and_data(parameter_str)
        
        header_hex = self._parsing_header(header_str)
        data_hex = self._parsing_data(data_str)

        header = self._convert_header(header_hex)
        data = self._convert_data(data_hex)

        self.header = header
        self.data = data
        self.content_str = parameter_str
        self.header_str = header_str
        self.data_str = data_str

        # print(self._convert_header(header))
        # print()
        # print(self._convert_data(data))
        # print()

    def _get_header_and_data(self, param_str):
        """
        Parameters
        ----------
        param_str: list
            Hex format contents enclosed by data size.
        
        Returns
        -------
        header_str: list
            Hex format header contents enclosed by data size.
        data_str: list
            Hex format data contents enclosed by data size.
        """
        header_str = param_str[:self._hdr_len]
        data_str = param_str[self._hdr_len:]
        return header_str, data_str

    def _parsing_header(self, header_str):
        """
        Parameters
        ----------
        header_str: list
            Hex format header contents enclosed by data size.
        
        Returns
        -------
        header: dict
            The types of values are hex.
        """
        # header = {}
        header = Header()
        header["magic_num"] = header_str[0]
        header["length"] = header_str[1]
        header["time"] = header_str[2]
        header["offset"] = header_str[3]
        return header

    def _parsing_data(self, data_str):
        """
        Parameters
        ----------
        data_str: list
            Hex format data contents enclosed by data size.
        
        Returns
        -------
        data: dict
            The types of values are hex.
        """
        data = {}
        data["num_of_range"] = data_str[0]
        data["radar_freq"] = data_str[1]
        data["transmit_beam_direction"] = [data_str[2], data_str[3]]
        data["nyquist_velocity"] = data_str[4]
        data["gps_locked"] = data_str[5]
        data["num_of_receiving_channels"] = data_str[6]
        
        channels = []
        num_channels = hex_to_int(data_str[6])
        for i in range(num_channels):
            channels.append(data_str[7+i])
        data["receiving_channels"] = channels
        
        return data

    def _convert_header(self, header):
        """
        Convert from hex to data ​​according to each data format.

        Parameters
        ----------
        header: dict
            The types of values are hex.
        
        Returns
        -------
        header: dict
            The types of values are data.
        """
        # header["magic_num"] = header["magic_num"]
        header["length"] = hex_to_int(header["length"])
        header["time"] = str(timestamp_to_datetime64(hex_to_int(header["time"])))
        header["offset"] = hex_to_int(header["offset"])
        return header

    #### ???: boolean 도 int로 변환?
    def _convert_data(self, data):
        """
        Convert from hex to data ​​according to each data format.

        Parameters
        ----------
        data: dict
            The types of values are hex.
        
        Returns
        -------
        data: dict
            The types of values are data.
        """
        data["num_of_range"] = hex_to_int(data["num_of_range"])
        data["radar_freq"] = hex_to_float(data["radar_freq"])
        data["transmit_beam_direction"] = [hex_to_int(x) for x in data["transmit_beam_direction"]]
        data["nyquist_velocity"] = hex_to_float(data["nyquist_velocity"])
        data["gps_locked"] = hex_to_int(data["gps_locked"])
        data["num_of_receiving_channels"] = hex_to_int(data["num_of_receiving_channels"])
        data["receiving_channels"] = [hex_to_int(x) for x in data["receiving_channels"]]
        return data

class IdbsAnalysedDataHDU(_IdbsHDU):
    def __init__(self, analysed_data_str):
        header_str, data_str = self._get_header_and_data(analysed_data_str)
        
        header_hex = self._parsing_header(header_str)
        data_hex = self._parsing_data(data_str)

        header = self._convert_header(header_hex)
        data = self._convert_data(data_hex)

        self.header = header
        self.data = data
        self.content_str = analysed_data_str
        self.header_str = header_str
        self.data_str = data_str
        # print(self._convert_header(header))
        # print()
        # print(self._convert_data(data))
        # print()

    def _get_header_and_data(self, data_str):
        """
        Parameters
        ----------
        data_str: list
            Hex format contents enclosed by data size.
        
        Returns
        -------
        header_str: list
            Hex format header contents enclosed by data size.
        data_str: list
            Hex format data contents enclosed by data size.
        """
        header_str = data_str[:self._hdr_len]
        data_str = data_str[self._hdr_len:]
        return header_str, data_str

    def _parsing_header(self, header_str):
        """
        Parameters
        ----------
        header_str: list
            Hex format header contents enclosed by data size.
        
        Returns
        -------
        header: dict
            The types of values are hex.
        """
        # header = {}
        header = Header()
        header["magic_num"] = header_str[0]
        header["length"] = header_str[1]
        header["time"] = header_str[2]
        header["offset"] = header_str[3]
        return header

    def _parsing_data(self, data_str):
        """
        Parameters
        ----------
        data_str: list
            Hex format data contents enclosed by data size.
        
        Returns
        -------
        data_list: list
            The types of values of data dict are hex.
            format: [data_dict, data_dict, data_dict ...]
        """
        data_list = []
        for i in range(0, len(data_str), 8):
            data = {}
            data["range"] = data_str[i]
            data["error_code"] = data_str[i+1]
            data["effective_beam_direction"] = [data_str[i+2], data_str[i+3]]
            data["radial_velocity"] = data_str[i+4]
            data["spectral_width"] = data_str[i+5]
            data["snr"] = data_str[i+6]
            data["power"] = data_str[i+7]
            data_list.append(data)
        
        return data_list
    
    ####### ???: timestamp를 str_date로 보여줘야하나?
    def _convert_header(self, header):
        """
        Convert from hex to data ​​according to each data format.

        Parameters
        ----------
        header: dict
            The types of values are hex.
        
        Returns
        -------
        header: dict
            The types of values are data.
        """
        # header["magic_num"] = header["magic_num"]
        header["length"] = hex_to_int(header["length"])
        header["time"] = str(timestamp_to_datetime64(hex_to_int(header["time"])))
        header["offset"] = hex_to_int(header["offset"])
        return header

    
    def _convert_data(self, data):
        """
        Convert from hex to data ​​according to each data format.

        Parameters
        ----------
        data: list
            The types of values of data dict are hex.
            format: [data_dict, data_dict, data_dict ...]
        
        Returns
        -------
        data: list
            The types of values of data dict are data.
            format: [data_dict, data_dict, data_dict ...]
        """
        for dt in data:
            dt["range"] = hex_to_float(dt["range"])
            dt["error_code"] = hex_to_int(dt["error_code"])
            dt["effective_beam_direction"] = [hex_to_float(x) for x in dt["effective_beam_direction"]]
            dt["radial_velocity"] = hex_to_float(dt["radial_velocity"])
            dt["spectral_width"] = hex_to_float(dt["spectral_width"])
            dt["snr"] = hex_to_float(dt["snr"])
            dt["power"] = hex_to_float(dt["power"])
        return data