import diagnostic_ascii
diagnostic = diagnostic_ascii.DiagnosticRAscii("diagnostic_r_20200130.txt")
print(diagnostic.header)
print(diagnostic.data)
# print(diagnostic.header_str)
# print(diagnostic.filepath)

print(diagnostic.size)
print(diagnostic.columns)
print(diagnostic.data[5][0])
# print(diagnostic.convert_object_to_datetime(diagnostic.data[5][0]))
# print(diagnostic.convert_object_to_datetime(diagnostic.header["Created"]))

# print(diagnostic_ascii.convert_key_letter_case(diagnostic.header, "u"))