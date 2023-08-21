# 필요 라이브러리와 모듈 내용 불러오기
from data_request import d_search, s_search

# 검색 방법 선택
print("1. Selective Search / 2. Direct Search")
search_input = input("Enter the number of search method: ")

if search_input == '1':
    s_search()
elif search_input == '2':
    d_search()
else:
    exit()