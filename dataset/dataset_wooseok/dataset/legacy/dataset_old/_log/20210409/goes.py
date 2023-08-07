import numpy as np

file_path = "20210316_Gp_part_5m.txt"

str_header = ""
str_data = ""
header = {}


data = None
names = ("date", "no", "P>1", "P>5", "P>10", "P>30", "P>50", "P>60", "P>100", "P>500", "E>2.0")
formats = ("U19", "i4", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8", "f8")




#
# 1. read file
#
fp = open(file_path, 'r')

# get str_header
line = fp.readline()
str_header += line
while(line != "" and "#----" not in line):
    line = fp.readline()
    str_header += line

# get str_data
line = fp.readline()
str_data += line
while(line != ""):
    line = fp.readline()
    str_data += line

fp.close()





#
# 2. create str_header (dict)
#

# parsing str_header (string)
# & extract key value in str_header
# & create header (dict)
# & get column names (for data) =====> 보류. 어차피 type은 알 수 없음. 하드코딩 해야할 것같음


# NOTE: 1. 규칙, 값 추출 어려움
#         - 1~4 번째줄
#         - title
#         - field
#             - 구분자가 \t가 아닌 띄어쓰기임 -> python의 split()으로 해결,
#             - date와 satellite no는 key이름 바꿀 것임
#       2. key이름 변형을 주고 싶음

label = []
columnes = ["date", "no"]
lines = str_header.split("\n")
for i, line in enumerate(lines):
    key, value = "", ""

    # remove '# '
    line = line.replace("# ", "")
    
    if(": " in line):
        key, value = line.split(": ")


    # NOTE: 임시
    if(i == 1):
        header["filename"] = value
        continue
    if(key == "Label"):
        label.append(value)
        continue
    # columnes
    if(i == len(lines)-3):
        columnes += line.split()[5:]
        continue
    
header["Label"] = label
# print(header)




#
# 3. create data (nd.array)
#

# parsing data (string)
lines = str_data.split("\n")
data_list=  []
for i, line in enumerate(lines):
    if(line == ""):
        continue
    value = line.split()
    # NOTE: date type: string or date?
    data_list.append((value[0]+"-"+value[1]+"-"+value[2]+" "+value[3][:2]+":"+value[3][2:]+":"+"00", value[4], value[5], value[6], value[7], value[8], value[9], value[10], value[11], value[12], value[13]))

# create data (nd.array)
data = np.array(data_list, dtype={'names':names, 'formats':formats})

print(data)


#
# 4. add information to header
#
header["object"] = "Sun"
header["observatory"] = "noaa"
header["obs_start_time"] = data["date"][0]
header["obs_end_time"] = data["date"][-1]
header["keycomments"] = {"object": "target object"}
#....


###########
'''
size() # shape(data)
field() # data.dtype.names
convert_string_to_date()
convert_key_letter_case()
plot() #matplotlib
'''