import requests

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
    
def remove_from_end(url, pop_str):
    if pop_str == 'skip':
        return url
    else:
        return url[:len(url) - len(pop_str)].rstrip()

def fetch_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Error occurred:", e)
        return None

def print_data(data):
    print('time: ' + data['time'] + ' / name: ' + data['name'])

def download_file(url, file_path):
    json_data = fetch_content(url)
    url = url.replace('search', 'download')
    if len(json_data['data_list']) == 1:
        if file_path == 'skip':
            file_path = '../dataset/' + json_data['data_list'][0]['name']
    else:
        if file_path == 'skip':
            url_data_line = url.split('?')[-1]
            url_data_list = url_data_line.split('&')
            url_dict = {}
            for url_data in url_data_list:
                key, value = url_data.split('=')
                url_dict[key] = value
            file_path = '../dataset/' + url_dict['table'] + '_' + url_dict['data_id'] + '_' + json_data['data_start_time'] + '_' + json_data['data_end_time'] + '.zip'
    with open(file_path, 'wb') as file:
        file.write(requests.get(url).content)
    print("Download completed from " + url)
    print("Data ID:", data_stack.stack[1]['data_id'])
    url = url.replace('download', 'search')
    
def show_table(url):
    table_json = fetch_content(url)
    print('-----Table List-----')
    for i, table in enumerate(table_json['data_table_list'], 1):
        print(str(i) + ': ' + table)
    table_input = input("Enter the table number / exit: ")
    if table_input == 'exit':
        return None
    else:
        table_url = '=' + table_json['data_table_list'][int(table_input) - 1]
        url = url + table_url
        url_stack.push(table_url)
        table_data = table_url.split('=')[-1]
        data_stack.push({'table': table_data})
        return url

def show_data_id(url):
    data_id_json = fetch_content(url)
    print('-----Data ID List-----')
    for i, data_id in enumerate(data_id_json['data_ids_list'], 1):
        print(str(i) + ': ' + data_id)
    data_id_input = input("Enter the data id number / exit / undo: ")
    if data_id_input == 'exit':
        return None
    elif data_id_input == 'undo':
        url = remove_from_end(url, url_stack.pop())
        data_stack.pop()
        return url
    else:
        data_id_url = '&data_id=' + data_id_json['data_ids_list'][int(data_id_input) - 1]
        url = url + data_id_url
        url_stack.push(data_id_url)
        data_id_data = data_id_url.split('=')[-1]
        data_stack.push({'data_id': data_id_data})
        return url

def show_start_time(url):
    start_time_json = fetch_content(url)
    print('-----Data Info-----')
    for key in start_time_json.keys():
        if start_time_json[key] == '':
            start_time_json[key] = 'None'
        print(key + ': ' + start_time_json[key])
    start_time_input = input("Enter the start time (YYYYMMDD) / exit / undo: ")
    if start_time_input == 'exit':
        return None
    elif start_time_input == 'undo':
        url = remove_from_end(url, url_stack.pop())
        data_stack.pop()
        return url
    else:
        start_time_url = '&start_time=' + start_time_input
        url = url + start_time_url
        url_stack.push(start_time_url)
        data_stack.push({'start_time': start_time_input})
        return url

def show_data_list(url):
    data_list_json = fetch_content(url)
    print('-----Data List-----')
    for key in data_list_json.keys():
        if key != 'data_list':
            print(key + ': ' + data_list_json[key])
        else:
            print(key + ': ')
            data_list = data_list_json[key]
            for data in data_list:
                print_data(data)
    if list(data_stack.peek().keys())[0] != 'end_time':
        end_time_input = input("Enter the end time (YYYYMMDD) / download / skip / exit / undo: ")
    else:
        end_time_input = input("Enter the download / exit / undo: ")
    if end_time_input == 'exit':
        return None
    elif end_time_input == 'undo':
        url = remove_from_end(url, url_stack.pop())
        data_stack.pop()
        return url
    elif end_time_input == 'skip':
        url_stack.push('skip')
        data_stack.push({'end_time': None})
        return url
    elif end_time_input == 'download':
        file_path = input("Enter the file path / skip: ")
        download_file(url, file_path)
        return url
    else:
        end_time_url = '&end_time=' + end_time_input
        url = url + end_time_url
        url_stack.push(end_time_url)
        data_stack.push({'end_time': end_time_input})
        return url

data_stack = Stack()
url_stack = Stack()

def s_search():
    url = 'http://swds.kasi.re.kr/swpipeline/api/search.php?table'
    while True:
        print()
        if data_stack.is_empty():
            url = show_table(url)
            if url == None:
                break
        else:
            data_key = list(data_stack.peek().keys())[0]
            if data_key == 'table':
                url = show_data_id(url)
                if url == None:
                    break
            elif data_key == 'data_id':
                url = show_start_time(url)
                if url == None:
                    break
            elif data_key == 'start_time' or data_key == 'end_time':
                url = show_data_list(url)
                if url == None:
                    break

def d_search():
    while True:
        file_info = input("Enter the file info(table name, data id, start time, end time (can be skipped)) / exit: ")
        if file_info == 'exit':
            break
        else:
            info_list = [info.strip() for info in file_info.split(',')]
            url = 'http://swds.kasi.re.kr/swpipeline/api/search.php?table' + '=' + info_list[0] + '&data_id=' + info_list[1] + '&start_time=' + info_list[2]
            if len(info_list) == 4:
                url = url + '&end_time=' + info_list[3]
            file_path = input("Enter the file path / skip: ")
            download_file(url, file_path)