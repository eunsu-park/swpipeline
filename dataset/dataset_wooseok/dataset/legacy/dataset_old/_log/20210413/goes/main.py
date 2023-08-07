import goes_ascii
from datetime import datetime
goes = goes_ascii.PartAscii("20210316_Gp_part_5m.txt")

print(goes.__doc__)

print(goes)

print(goes.header)
# print(goes.data)
# print(goes.header_str)
# print(goes.filepath)

print(goes.size)
print(goes.columns)
print(goes.data[5][0])


# NOTE
# 참고:https://www.w3schools.com/python/numpy/numpy_array_filter.asp
# 
print(goes.data[(goes.data["Date"] > datetime(2021,3,16,1,20)) & (goes.data["Date"] < datetime(2021,3,16,15,45))])

# print(goes_ascii.sort(goes.data, "Date", reversed=True))
# print(goes.convert_object_to_datetime(goes.data[5][0]))
# print(goes.convert_object_to_datetime(goes.header["Created"]))

# print(goes_ascii.convert_key_letter_case(goes.header, "u"))