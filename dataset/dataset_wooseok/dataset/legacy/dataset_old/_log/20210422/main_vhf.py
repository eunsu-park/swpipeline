import dataset.vhf_emdr.iono as iono
import os

test_source_dir = "./test_source"


iono_e = iono.Iono(os.path.join(test_source_dir, "20210103_iono_e.idbs"))
# print(iono_e)
# print(iono_e.idbs_hdu_list)
print(iono_e.idbs_hdu_list[0].header)

# print(iono_e.header)
# print(iono_e.info())
# print(iono_e.data.dtype.names)
# print(iono_e.data)
# print(iono_e.data.dtype.names)

# iono_e.info()

# print(iono_e.header_str)
# print(iono_e.filepath)

# print(iono_e.size)
# print(iono_e.data[5][0])



# print(iono_e.convert_object_to_datetime("2013-05-01T10:00:00Z"))
# print(iono_e.convert_object_to_datetime("2013-05-01T10:00:00.34Z"))
# print(iono_e.convert_object_to_datetime("2013-05-01T09:59:56.50Z"))

# print(iono_e.convert_object_to_datetime("1977.01.01_00:00:00_TAI"))
# print(iono_e.convert_object_to_datetime("2013-05-09T20:27:21"))
# print(iono_e.convert_object_to_datetime("2013-05-01T09:59:59.34"))

# print(iono_e.convert_key_letter_case("u"))