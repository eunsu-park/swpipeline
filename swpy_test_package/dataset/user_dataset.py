from search_dataset import *

file_path = None
data_id = None

# 파일 검색 방법 선택: 1. 파일 탐색기 사용 / 2. 파일 경로 직접 입력
file_path_num = int(input("Enter the number of file search method (1. use file explorer / 2. enter the file path directly): "))
if file_path_num == 1:
    file_path = file_explorer()
elif file_path_num == 2:
    file_path = input("Enter the file path: ")
else:
    exit()

# 데이터 아이디 검색 방법 선택: 1. 데이터 아이디 리스트 조회 / 2. 데이터 아이디 직접 입력
data_id_num = int(input("Enter the number of data id search method (1. use data id list / 2. enter the data id directly): "))
if data_id_num == 1:
    data_id = data_id_explorer()
elif data_id_num == 2:
    data_id = input("Enter the data id: ")
else:
    exit()

# 조회 데이터 선택: 1. 헤더 / 2. 데이터 / 3. 헤더+데이터 / 4. 시각화 / 5. 1~4 모두 조회
info_num = int(input("Enter the number of information (1. header / 2. data / 3. header + data / 4. plot / 5. all): "))
dataset = search(file_path, data_id, info_num)