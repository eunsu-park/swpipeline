from dataset.vhf_emdr.hdu import *
import numpy as np

# bigger endian, unsigned int
def hex_to_int(hex):
    return int(hex,16)

filepath = "./test_source/20210103_iono_e.idbs"

pri_hdr_magic_num = "20000000"
param_hdr_magic_num = "20a00000"
data_hdr_magic_num = "20a10000"

hdr_len = 4
byte_group = 8

# for record
len_info_idx = 1
offset_info_idx = 3

pri_hdr_str = ""
param_hdr_str = ""
param_record_str = ""
data_hdr_str = ""
data_record_str = ""


class Iono:
    def __init__(self, filepath):
        self._data_size = 8 # byte

        hex_str = self.load(filepath)
        hdu_list = self.parsing_hex(hex_str)
        
        self.hdu_list = hdu_list
        ######
        self.header = self.parsing_header(hdu_list)
        self.data = self.parsing_data(hdu_list)


    def load(self, filepath):
        hex_str = ""
        # read
        with open(filepath, "rb") as f:
            hex_str = f.read().hex()
        
        # grouping with data size
        hex_str = [hex_str[i:i+self._data_size] for i in range(0, int(len(hex_str)), self._data_size)]
        return hex_str


    # [PrimaryHDU, (ParameterHDU, AnalysedDataHDU), (ParameterHDU, AnalysedDataHDU)...]
    def parsing_hex(self, hex_str):
        hdu_list = []
        #
        # get primary header
        if(hex_str[0] != pri_hdr_magic_num):
            print("file format error")
        pri_hdr_str = hex_str[:hdr_len]
        hdu_list.append(PrimaryHDU(pri_hdr_str))
        
        #
        # get header and record of parameter and analysed data
        s_offset = hdr_len
        set_ = ()
        while(s_offset < len(hex_str)):
            # paramter
            if(hex_str[s_offset] != param_hdr_magic_num):
                print("file format error")
                return None
                # break
                
            param_hdr_str = hex_str[s_offset:s_offset+hdr_len]
            param_record_len = int(hex_to_int(hex_str[s_offset+len_info_idx])/(byte_group/2))
            param_record_offset = int(hex_to_int(hex_str[s_offset+offset_info_idx])/(byte_group/2))
            param_record_str = hex_str[param_record_offset:(param_record_offset+param_record_len)]

            param_str = param_hdr_str + param_record_str

            # analysed data
            s_offset = param_record_offset+param_record_len
            if(hex_str[s_offset] != data_hdr_magic_num):
                print("data is not exist")
                if(hex_str[s_offset] == param_hdr_magic_num):
                    set_ = (ParameterHDU(param_str),)
                    hdu_list.append(set_)
                    continue
                else:
                    print("file format error")
                    return None
                    # break
            
            data_hdr_str = hex_str[s_offset:s_offset+hdr_len]
            data_record_len = int(hex_to_int(hex_str[s_offset+len_info_idx])/(byte_group/2))
            data_record_offset = int(hex_to_int(hex_str[s_offset+offset_info_idx])/(byte_group/2))
            data_record_str = hex_str[data_record_offset:(data_record_offset+data_record_len)]
            
            data_str = data_hdr_str + data_record_str

            s_offset = data_record_offset+data_record_len

            set_ = (ParameterHDU(param_str), AnalysedDataHDU(data_str))
            hdu_list.append(set_)
        return hdu_list
    

    def parsing_header(self, hdu_list):
        # PrimaryHDU
        return hdu_list[0].header_cvt


    ## ??: list는 어떻게 해야하지 이것도 풀어서 써야하나?
    ##     channel은 계속 바뀔 수 있음
    ## 데이터가 없다면? -99999?
    def parsing_data(self, hdu_list):
        # set
        # ㄴParamterHDU
        # ㄴAnalysedDataHDU

        if(isinstance(hdu_list[0], PrimaryHDU)):
            hdu_list.pop(0)

        # data["num_of_range"] = hex_to_int(data["num_of_range"])
        # data["radar_freq"] = hex_to_float(data["radar_freq"])
        # data["transmit_beam_direction"] = [hex_to_int(x) for x in data["transmit_beam_direction"]]
        # data["nyquist_velocity"] = hex_to_float(data["nyquist_velocity"])
        # data["gps_locked"] = hex_to_int(data["gps_locked"]) #### boolean
        # data["num_of_receiving_channels"] = hex_to_int(data["num_of_receiving_channels"])
        # data["receiving_channels"] = [hex_to_int(x) for x in data["receiving_channels"]]
        # dt["range"] = hex_to_float(dt["range"])
        # dt["error_code"] = hex_to_int(dt["error_code"])
        # dt["effective_beam_direction"] = [hex_to_float(x) for x in dt["effective_beam_direction"]]
        # dt["radial_velocity"] = hex_to_float(dt["radial_velocity"])
        # dt["spectral_width"] = hex_to_float(dt["spectral_width"])
        # dt["snr"] = hex_to_float(dt["snr"])
        # dt["power"] = hex_to_float(dt["power"])

        names = ("time", "range", "error_code", "effective_beam_direction", "radial_velocity", "spectral_width", "snr", "power", "num_of_range", "radar_freq", "transmit_beam_direction", "nyquist_velocity", "gps_locked", "num_of_receiving_channels", "receiving_channels")
        formats = ("i4", "f8", "i4", "object", "f8", "f8", "f8", "f8", "i4", "f8", "object", "f8", "i4", "i4", "object")
        
        data_tuples = []
        for param, data in hdu_list:
            time = param.header_cvt["time"]
            if(time != data.header_cvt["time"]):
                print("error")
                return None
            
            prm = param.data_cvt
            for dt in data.data_cvt:
                data_tuple = (time,)
                data_tuple += (dt["range"], dt["error_code"], dt["effective_beam_direction"], dt["radial_velocity"], dt["spectral_width"], dt["snr"], dt["power"],)
                data_tuple += (prm["num_of_range"], prm["radar_freq"], prm["transmit_beam_direction"], prm["nyquist_velocity"], prm["gps_locked"], prm["num_of_receiving_channels"], prm["receiving_channels"])
                
                data_tuples.append(data_tuple)
        
        data = np.array(data_tuples, dtype={'names':names, 'formats':formats})
        print(data.dtype)
        print(data)
        return data


    def add_info_to_header(self, header):
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
        header["Institute"] = "Kasi"
        # header["Object"] = "Sun"
        # header["Src_url"] = "https://services.swpc.noaa.gov/json/goes/primary"
        header["Comment"] = ""
        header["History"] = ""
        # header["Keycomments"] = {
        #                         "Location": "Longitude of satellite.",
        #                         }

        return header


iono = Iono(filepath)
# print(iono.header)
# print(iono.hdu_list)


# with open(filepath, "rb") as f:
    # hex_str = f.read().hex()
    # hex_list = [hex_str[i:i+byte_group] for i in range(0, int(len(hex_str)), 8)]

# #
# # get primary header
# if(hex_list[0] != pri_hdr_magic_num):
#     print("file format error")
# pri_hdr_str = hex_list[:hdr_len]

# #
# # get header and record of parameter and analysed data
# s_offset = hdr_len
# while(s_offset < len(hex_list)):
#     # paramter
#     if(hex_list[s_offset] != param_hdr_magic_num):
#         print("file format error")
#         break
        
#     param_hdr_str = hex_list[s_offset:s_offset+hdr_len]
#     param_record_len = int(hex_to_int(hex_list[s_offset+len_info_idx])/(byte_group/2))
#     param_record_offset = int(hex_to_int(hex_list[s_offset+offset_info_idx])/(byte_group/2))
#     param_record_str = hex_list[param_record_offset:(param_record_offset+param_record_len)]


#     # analysed data
#     s_offset = param_record_offset+param_record_len
#     if(hex_list[s_offset] != data_hdr_magic_num):
#         print("data is not exist")
#         if(hex_list[s_offset] == param_hdr_magic_num):
#             continue
#         else:
#             print("file format error")
#             break
#             # return
    
#     data_hdr_str = hex_list[s_offset:s_offset+hdr_len]
#     data_record_len = int(hex_to_int(hex_list[s_offset+len_info_idx])/(byte_group/2))
#     data_record_offset = int(hex_to_int(hex_list[s_offset+offset_info_idx])/(byte_group/2))
#     data_record_str = hex_list[data_record_offset:(data_record_offset+data_record_len)]

#     s_offset = data_record_offset+data_record_len


'''
# try2
with open(filepath, "rb") as f:
    hex_str = f.read().hex()
    hex_list = [hex_str[i:i+byte_group] for i in range(0, int(len(hex_str)), 8)]

    #
    # get primary header
    if(hex_list[0] != pri_hdr_magic_num):
        print("file format error")
    pri_hdr_str = hex_list[:hdr_len]

    #
    # get header and record of parameter and analysed data
    s_offset = hdr_len
    while(s_offset < len(hex_list)):
        # paramter
        if(hex_list[s_offset] != param_hdr_magic_num):
            print("file format error")
            break
            
        param_hdr_str = hex_list[s_offset:s_offset+hdr_len]
        param_record_len = int(hex_to_int(hex_list[s_offset+len_info_idx])/(byte_group/2))
        param_record_offset = int(hex_to_int(hex_list[s_offset+offset_info_idx])/(byte_group/2))
        param_record_str = hex_list[param_record_offset:(param_record_offset+param_record_len)]


        # analysed data
        s_offset = param_record_offset+param_record_len
        if(hex_list[s_offset] != data_hdr_magic_num):
            print("data is not exist")
            if(hex_list[s_offset] == param_hdr_magic_num):
                continue
            else:
                print("file format error")
                break
                # return
        
        data_hdr_str = hex_list[s_offset:s_offset+hdr_len]
        data_record_len = int(hex_to_int(hex_list[s_offset+len_info_idx])/(byte_group/2))
        data_record_offset = int(hex_to_int(hex_list[s_offset+offset_info_idx])/(byte_group/2))
        data_record_str = hex_list[data_record_offset:(data_record_offset+data_record_len)]

        s_offset = data_record_offset+data_record_len
'''



'''
# try1

if(hex_list[:byte_group] != pri_hdr_magic_num):
    print("file format error")
pri_hdr_str = hex_list[:byte_group*4]


param_hdr_idx = hex_list.index(param_hdr_magic_num, 1)
param_hdr_str = hex_list[param_hdr_idx:param_hdr_idx+(byte_group*4)]
param_record_len = int(param_hdr_str[1*byte_group:2*byte_group],16)*2
param_record_offset = int(param_hdr_str[3*byte_group:4*byte_group],16)*2
param_record_str = hex_list[param_record_offset:(param_record_offset+param_record_len)]
print(pri_hdr_str)
print(param_hdr_str)
print(param_record_len)
print(param_record_offset)
print(param_record_str)
data_hdr_idx = hex_list.index(data_hdr_magic_num, 1)
data_hdr_str = hex_list[data_hdr_idx:data_hdr_idx+(byte_group*4)]
data_record_len = int(data_hdr_str[1*byte_group:2*byte_group],16)*2
data_record_offset = int(data_hdr_str[3*byte_group:4*byte_group],16)*2
data_record_str = hex_list[data_record_offset:(data_record_offset+data_record_len)]
print(data_hdr_str)
print(data_record_len)
print(data_record_offset)
print(data_record_str)
# idbs_header["magic_num"] = hex_list[0]
# idbs_header["num_of_record"] = hex_list[1]
# idbs_header["start_date"] = hex_list[2]
# idbs_header["end_date"] = hex_list[3]
'''



    # # 파일이 들어오다만 경우라면 문제가 될 수 있음
    # print(len(hex_list)/4)
    # for i in range(int(len(hex_list)/4)):
    #     j = i*4
    #     asdf.append(hex_list[j:j+4])
    # # print(hex_list.hex())
    # # # NOTE: f.readlines(): contains "\n"
    # # for line in f.read().splitlines():
    # #     if(line[0] in header_delimiters):
    # #         header_lines.append(line)
    # #         continue
    # #     data_lines.append(line)

