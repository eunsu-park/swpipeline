import goes_ascii
goes = goes_ascii.read("20210316_Gp_part_5m.txt")
print(goes.header)
print(goes.data)
# print(goes.header_str)
# print(goes.filepath)

print(goes.size)
print(goes.columns)
print(goes.data[5][0])
print(goes.convert_object_to_datetime(goes.data[5][0]))
print(goes.convert_object_to_datetime(goes.header["date"]))

# print(goes_ascii.convert_key_letter_case(goes.header, "u"))