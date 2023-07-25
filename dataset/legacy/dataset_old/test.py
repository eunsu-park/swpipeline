from dataset.lib.utilities import *
import os

test_source_dir = "./test_source"

delimiters = ["#", ":"]
lines = read_file(os.path.join(test_source_dir, "20210316_Gp_part_5m.txt"))
header_end_line_idx = find_header_end_line_idx(lines, delimiters)
header_lines, data_lines = divide_heaeder_and_data(lines, header_end_line_idx)
# print(header_end_line_idx)
# print(header_lines)
# print(data_lines)

header_lines = remove_header_delimiters(header_lines, delimiters)
# print(header_lines)

data_lines = divide_data_ele(data_lines, "ws")
# print(data_lines)

# remove columns + parsing header
header = parsing_header(header_lines[:-3], ":")
print(header)


# header_lines = remove_header_column_info(header_lines, -3)
# print(header_lines)
