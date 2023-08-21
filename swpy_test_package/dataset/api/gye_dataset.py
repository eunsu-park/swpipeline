# -*- coding: utf-8 -*-
"""
gye_dataset_log.py
"""

# 필요 라이브러리, 모듈 내용 불러오기
from .base_dataset import BaseDataset
import numpy as np
import matplotlib.pyplot as plt

class GyeDataset(BaseDataset):
    """
    GYE 데이터 셋 기본 클래스
    - 추상 클래스 BaseDataset 내용 구현
    """
    def __init__(self, file_):
        super(GyeDataset, self).__init__(file_)

class GyeChannelDataset(GyeDataset):
    """
    'channel.log' 파일 데이터 셋 클래스
    - GyeDataset 클래스 내용 구현
    """
    def __init__(self, file_):
        """
        생성자 함수
        - file_: 파일 경로
        - header: 헤더 정보
        - data: 데이터 정보
        - all: 헤더+데이터 정보
        """
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        """
        전체 데이터 파싱 함수
        - 헤더 내용이 없어 데이터 부분만 분류
        - 분류 후 각 정보별 파싱 함수 호출
        """
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        """
        헤더 부분 파싱 함수
        - header에 내용 저장
        """
        self.header = header

    def parsing_data(self, data):
        """
        데이터 부분 파싱 함수
        - 각 줄의 위치별로 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        float_index = [0, 3, 4, 5, 6, 7]
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i not in float_index:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i not in float_index:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64)))

        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        """
        헤더+데이터 부분 파싱 함수
        - 헤더, 데이터 정보를 리스트에 추가하여 all에 저장
        """
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        """
        데이터 시각화 함수
        - 조회 데이터 구간 입력, 미입력 시 전체 구간 조회
        - 데이터 종류별 개별 시각화 여부 입력
        - 개별 시각화의 경우 종류별로 분할
        - 통합 시각화의 경우 스케일링 후 종류별로 색을 통해 분류
        """
        names = self.data.dtype.names
        start_default = self.data[names[2]][0]
        end_default = self.data[names[2]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[2]] >= start) & (self.data[names[2]] <= end)]
        dates = filtered_data[names[2]]
        values_name = ['Col1', 'Col2'] + ['Col' + str(i) for i in range(4, 14)]

        if show_seperate:
            fig, axs = plt.subplots(3, 4, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 4, i % 4
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                if row == 2:
                    ax.set_xlabel('Date')
                if col == 0:
                    ax.set_ylabel('Value')
                ax.set_title(name)
                ax.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            for i, name in enumerate(values_name):
                values = np.array(filtered_data[name])
                values[np.isnan(values)] = np.nanmean(values)
                values = (values - np.min(values)) / (np.max(values) - np.min(values))
                plt.plot(dates, values, label = name)
            plt.xlabel('Date')
            plt.ylabel('Value (Min-Max Scaling)')
            plt.title('Gye Scint Channel')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()

class GyeIonoDataset(GyeDataset):
    """
    'iono.log' 파일 데이터 셋 클래스
    - GyeDataset 클래스 내용 구현
    """
    def __init__(self, file_):
        """
        생성자 함수
        - file_: 파일 경로
        - header: 헤더 정보
        - data: 데이터 정보
        - all: 헤더+데이터 정보
        """
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        """
        전체 데이터 파싱 함수
        - 헤더 내용이 없어 데이터 부분만 분류
        - 분류 후 각 정보별 파싱 함수 호출
        """
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        """
        헤더 부분 파싱 함수
        - header에 내용 저장
        """
        self.header = header

    def parsing_data(self, data):
        """
        데이터 부분 파싱 함수
        - 각 줄의 위치별로 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i == 0 or i == 4:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)
        
        for i in range(len(data_line_list[0])):
            if i == 0 or i == 4:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64)))

        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        """
        헤더+데이터 부분 파싱 함수
        - 헤더, 데이터 정보를 리스트에 추가하여 all에 저장
        """
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        """
        데이터 시각화 함수
        - 조회 데이터 구간 입력, 미입력 시 전체 구간 조회
        - 데이터 종류별 개별 시각화 여부 입력
        - 개별 시각화의 경우 종류별로 분할
        - 통합 시각화의 경우 스케일링 후 종류별로 색을 통해 분류
        """
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[1]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['Col' + str(i) for i in range(2, 6)]

        if show_seperate:
            fig, axs = plt.subplots(2, 2, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 2, i % 2
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                ax.set_xlabel('Date')
                ax.set_ylabel('Value')
                ax.set_title(name)
                ax.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            for i, name in enumerate(values_name):
                values = np.array(filtered_data[name])
                values[np.isnan(values)] = np.nanmean(values)
                values = (values - np.min(values)) / (np.max(values) - np.min(values))
                plt.plot(dates, values, label = name)
            plt.xlabel('Date')
            plt.ylabel('Value (Min-Max Scaling)')
            plt.title('Gye Scint Iono')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()

class GyeNavsolDataset(GyeDataset):
    """
    'navsol.log' 파일 데이터 셋 클래스
    - GyeDataset 클래스 내용 구현
    """
    def __init__(self, file_):
        """
        생성자 함수
        - file_: 파일 경로
        - header: 헤더 정보
        - data: 데이터 정보
        - all: 헤더+데이터 정보
        """
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        """
        전체 데이터 파싱 함수
        - 헤더 내용이 없어 데이터 부분만 분류
        - 분류 후 각 정보별 파싱 함수 호출
        """
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        """
        헤더 부분 파싱 함수
        - header에 내용 저장
        """
        self.header = header
    
    def parsing_data(self, data):
        """
        데이터 부분 파싱 함수
        - 각 줄의 위치별로 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i == 0 or i == 10:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)
        
        for i in range(len(data_line_list[0])):
            if i == 0 or i == 10:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64)))

        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        """
        헤더+데이터 부분 파싱 함수
        - 헤더, 데이터 정보를 리스트에 추가하여 all에 저장
        """
        all = [self.header, self.data]
        self.all = all
    
    def plot(self):
        """
        데이터 시각화 함수
        - 조회 데이터 구간 입력, 미입력 시 전체 구간 조회
        - 데이터 종류별 개별 시각화 여부 입력
        - 개별 시각화의 경우 종류별로 분할
        - 통합 시각화의 경우 스케일링 후 종류별로 색을 통해 분류
        """
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['Col' + str(i) for i in range(2, 12)]

        if show_seperate:
            fig, axs = plt.subplots(5, 2, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 2, i % 2
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                if row == 4:
                    ax.set_xlabel('Date')
                ax.set_ylabel('Value')
                ax.set_title(name)
                ax.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            for i, name in enumerate(values_name):
                values = np.array(filtered_data[name])
                values[np.isnan(values)] = np.nanmean(values)
                values = (values - np.min(values)) / (np.max(values) - np.min(values))
                plt.plot(dates, values, label = name)
            plt.xlabel('Date')
            plt.ylabel('Value (Min-Max Scaling)')
            plt.title('Gye Scint Navsol')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()

class GyeScintDataset(GyeDataset):
    """
    'scint.log' 파일 데이터 셋 클래스
    - GyeDataset 클래스 내용 구현
    """
    def __init__(self, file_):
        """
        생성자 함수
        - file_: 파일 경로
        - header: 헤더 정보
        - data: 데이터 정보
        - all: 헤더+데이터 정보
        """
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        """
        전체 데이터 파싱 함수
        - 헤더 내용이 없어 데이터 부분만 분류
        - 분류 후 각 정보별 파싱 함수 호출
        """
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        """
        헤더 부분 파싱 함수
        - header에 내용 저장
        """
        self.header = header

    def parsing_data(self, data):
        """
        데이터 부분 파싱 함수
        - 각 줄의 위치별로 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i == 0 or i == 11 or i == 12 or i == 13:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i == 0 or i == 11 or i == 12 or i == 13:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64)))

        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        """
        헤더+데이터 부분 파싱 함수
        - 헤더, 데이터 정보를 리스트에 추가하여 all에 저장
        """
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        """
        데이터 시각화 함수
        - 조회 데이터 구간 입력, 미입력 시 전체 구간 조회
        - 데이터 종류별 개별 시각화 여부 입력
        - 개별 시각화의 경우 종류별로 분할
        - 통합 시각화의 경우 스케일링 후 종류별로 색을 통해 분류
        """
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['Col' + str(i) for i in range(2, 15)]
        del values_name[1]

        if show_seperate:
            fig, axs = plt.subplots(3, 4, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 4, i % 4
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                if row == 2:
                    ax.set_xlabel('Date')
                if col == 0:
                    ax.set_ylabel('Value')
                ax.set_title(name)
                ax.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            for i, name in enumerate(values_name):
                values = np.array(filtered_data[name])
                values[np.isnan(values)] = np.nanmean(values)
                values = (values - np.min(values)) / (np.max(values) - np.min(values))
                plt.plot(dates, values, label = name)
            plt.xlabel('Date')
            plt.ylabel('Value (Min-Max Scaling)')
            plt.title('Gye Scint Scint')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()

class GyeTxinfoDataset(GyeDataset):
    """
    'txinfo.log' 파일 데이터 셋 클래스
    - GyeDataset 클래스 내용 구현
    """
    def __init__(self, file_):
        """
        생성자 함수
        - file_: 파일 경로
        - header: 헤더 정보
        - data: 데이터 정보
        - all: 헤더+데이터 정보
        """
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        """
        전체 데이터 파싱 함수
        - 헤더 내용이 없어 데이터 부분만 분류
        - 분류 후 각 정보별 파싱 함수 호출
        """
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        """
        헤더 부분 파싱 함수
        - header에 내용 저장
        """
        self.header = header

    def parsing_data(self, data):
        """
        데이터 부분 파싱 함수
        - 각 줄의 위치별로 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i not in [1, 2, 3]:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i not in [1, 2, 3]:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64)))

        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        """
        헤더+데이터 부분 파싱 함수
        - 헤더, 데이터 정보를 리스트에 추가하여 all에 저장
        """
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        """
        데이터 시각화 함수
        - 조회 데이터 구간 입력, 미입력 시 전체 구간 조회
        - 데이터 종류별 개별 시각화 여부 입력
        - 개별 시각화의 경우 종류별로 분할
        - 통합 시각화의 경우 스케일링 후 종류별로 색을 통해 분류
        """
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['Col' + str(i) for i in range(2, 8)]

        if show_seperate:
            fig, axs = plt.subplots(2, 3, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 3, i % 3
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                ax.set_xlabel('Date')
                ax.set_ylabel('Value')
                ax.set_title(name)
                ax.grid(True)
            plt.tight_layout()
            plt.show()
        else:
            for i, name in enumerate(values_name):
                values = np.array(filtered_data[name])
                values[np.isnan(values)] = np.nanmean(values)
                values = (values - np.min(values)) / (np.max(values) - np.min(values))
                plt.plot(dates, values, label = name)
            plt.xlabel('Date')
            plt.ylabel('Value (Min-Max Scaling)')
            plt.title('Gye Scint Txinfo')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()