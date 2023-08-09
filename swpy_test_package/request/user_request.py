from data_request import d_search, s_search

print("1. Selective Search / 2. Direct Search")
search_input = input("Enter the number of search method: ")

if search_input == '1':
    s_search()
elif search_input == '2':
    d_search()
else:
    exit()