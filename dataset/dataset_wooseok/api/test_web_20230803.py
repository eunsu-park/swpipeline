import requests
import json

class Stack:
    def __init__(self):
        self.stack = []

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        if not self.is_empty():
            return self.stack.pop()
        else:
            return None

    def peek(self):
        if not self.is_empty():
            return self.stack[-1]
        else:
            return None

    def is_empty(self):
        return len(self.stack) == 0

    def size(self):
        return len(self.stack)
    
def remove_from_end(url, length):
    return url[:len(url) - length].rstrip()

def show_web_content(url):
    print(url)
    web_content = fetch_web_content(url)
    if web_content:
        for key in web_content.keys():
            print(key, web_content[key])

stack = Stack()
url = 'http://swds.kasi.re.kr/swpipeline/api/search.php?table'
flag = True

def fetch_web_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return None

show_web_content(url)

while flag:
    input_str = input("Enter the path: ")
    if input_str == 'exit':
        flag = False
    elif input_str == 'undo':
        url = remove_from_end(url, len(stack.pop()))
        show_web_content(url)
    elif input_str == 'download':
        json_data = fetch_web_content(url)
        stack.push(input_str)
        url = url.replace('search', 'download')
        if len(json_data['data_list']) == 1:
            file_name = json_data['data_list'][0]['name']
            with open(file_name, 'wb') as file:
                file.write(requests.get(url).content)
        else:
            url_data_line = url.split('?')[-1]
            url_data_list = url_data_line.split('&')
            url_dict = {}
            for url_data in url_data_list:
                key, value = url_data.split('=')
                url_dict[key] = value
            file_name = url_dict['table'] + '_' + url_dict['data_id'] + '_' + json_data['data_start_time'] + '_' + json_data['data_end_time'] + '.zip'
            with open(file_name, 'wb') as file:
                file.write(requests.get(url).content)
        url = url.replace('download', 'search')
        stack.pop()
        show_web_content(url)
    else:
        stack.push(input_str)
        url = url + stack.peek()
        show_web_content(url)

# 종료하기 전까지 경로 입력 반복
# 스택 사용하여 url 접근 혹은 취소
# exit 입력 시 종료
# undo 입력 시 이전 명령 취소
# download 입력 시 search -> download 변환하여 파일 다운로드 후 다시 download -> search 변환