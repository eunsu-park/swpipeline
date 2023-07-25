
import dataset.ace as ace

from datetime import datetime
import os

test_source_dir = "./test_source"

print("========== ACE MAG ==========")
mag = ace.open(os.path.join(test_source_dir, "20010807_ace_mag_1m.txt"))


print("========== ACE SIS ==========")
sis = ace.open(os.path.join(test_source_dir, "20010807_ace_sis_5m.txt"))


print("========== ACE SWEPAM ==========")
swepam = ace.open(os.path.join(test_source_dir, "20010807_ace_swepam_1m.txt"))
