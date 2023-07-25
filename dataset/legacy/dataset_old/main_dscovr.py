
# import dataset.goes.goes as goes
import dataset.dscovr as dscovr

from datetime import datetime
import os

test_source_dir = "./test_source"

print("========== Magnetic field ==========")
file_ = os.path.join(test_source_dir, "dscovr_mag_20220922.txt")
mag = dscovr.open(file_)



print(mag)
mag.info()

print(mag.header)
print(mag.data.dtype.names)

print(mag.data)

print()
print("========== Plasma ==========")

plasma = dscovr.open(os.path.join(test_source_dir, "dscovr_plasma_20220922.txt"))
print(plasma)


print(plasma)
plasma.info()

print(plasma.header)
print(plasma.data.dtype.names)

print(plasma.data)



# print(xray.header)
# print(xray.data)
# # print(xray.header_str)
# # print(xray.filepath)

# print(xray.size)
# print(xray.columns)
# # print(xray.data[5][0])

#print()
#print("========== Geomag ==========")

#geomag = goes.open(os.path.join(test_source_dir, "20210316_Gp_mag_1m.txt"))
# print(geomag)
# geomag.info()

# print(geomag.header)
# print(geomag.data)
# # print(geomag.header_str)
# # print(geomag.filepath)

# print(geomag.size)
# print(geomag.columns)
# # print(geomag.data[5][0])
