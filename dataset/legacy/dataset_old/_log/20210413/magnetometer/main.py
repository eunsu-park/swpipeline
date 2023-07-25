import magnetometer_ascii
mm = magnetometer_ascii.MagnetometerAscii("gm_boh_sec5_20210409.txt")
print(mm.header)
print(mm.data)
# print(mm.header_str)
# print(mm.filepath)

print(mm.size)
print(mm.columns)
print(mm.data[5][0])
# print(mm.convert_object_to_datetime(mm.data[5][0]))
# print(mm.convert_object_to_datetime(mm.header["Created"]))

# print(mm_ascii.convert_key_letter_case(mm.header, "u"))