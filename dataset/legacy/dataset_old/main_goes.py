
# import dataset.goes.goes as goes
import dataset.goes as goes

from datetime import datetime
import os

test_source_dir = "./test_source"

print("========== Particle ==========")
particle = goes.open(os.path.join(test_source_dir, "20210316_Gp_part_5m.txt"))

# print(goes.__doc__)

# print(particle)
# particle.info()

# print(particle.header)
print(particle.data.dtype.names)

# # print(particle.header_preview())
# print(particle.data)
# print(particle.header_str)
# # print(particle.filepath)

# print(particle.size)
# print(particle.columns)
# # print(particle.data[5][0])

# # NOTE
# # 참고:https://www.w3schools.com/python/numpy/numpy_array_filter.asp
# # 
# # print(particle.data[(particle.data["Date"] > datetime(2021,3,16,1,20)) & (particle.data["Date"] < datetime(2021,3,16,15,45))])

# # print(particle.sort(particle.data, "Date", reversed=True))
# # print(particle.convert_object_to_datetime(particle.data[5][0]))
# # print(particle.convert_object_to_datetime(particle.header["Created"]))

# # print(particle.convert_key_letter_case(particle.header, "u"))

print()
print("========== Xray ==========")

xray = goes.open(os.path.join(test_source_dir, "20210316_Gp_xr_1m.txt"))
# print(xray)
# xray.info()

# print(xray.header)
# print(xray.data)
# # print(xray.header_str)
# # print(xray.filepath)

# print(xray.size)
# print(xray.columns)
# # print(xray.data[5][0])

print()
print("========== Geomag ==========")

geomag = goes.open(os.path.join(test_source_dir, "20210316_Gp_mag_1m.txt"))
# print(geomag)
# geomag.info()

# print(geomag.header)
# print(geomag.data)
# # print(geomag.header_str)
# # print(geomag.filepath)

# print(geomag.size)
# print(geomag.columns)
# # print(geomag.data[5][0])