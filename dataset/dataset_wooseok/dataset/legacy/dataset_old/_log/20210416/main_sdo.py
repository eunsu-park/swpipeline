import dataset.sdo.aia_fits as aia_fits
import os

test_source_dir = "./test_source"

aiafits = aia_fits.AIAFits(os.path.join(test_source_dir, "aia.lev1_171_2013-05-01T10_00_00Z_image_lev1.fits"))
print(aiafits.header)
print(aiafits.data)
print(aiafits.header_str)
print(aiafits.filepath)

print(aiafits.size)
print(aiafits.data[5][0])



# print(aiafits.convert_object_to_datetime("2013-05-01T10:00:00Z"))
# print(aiafits.convert_object_to_datetime("2013-05-01T10:00:00.34Z"))
# print(aiafits.convert_object_to_datetime("2013-05-01T09:59:56.50Z"))

# print(aiafits.convert_object_to_datetime("1977.01.01_00:00:00_TAI"))
# print(aiafits.convert_object_to_datetime("2013-05-09T20:27:21"))
# print(aiafits.convert_object_to_datetime("2013-05-01T09:59:59.34"))

# print(aiafits.convert_key_letter_case("u"))