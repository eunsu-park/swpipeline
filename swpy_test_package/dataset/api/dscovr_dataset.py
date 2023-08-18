# 필요 라이브러리, 모듈 내용 불러오기
from .base_dataset import BaseDataset
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

class DscovrDataset(BaseDataset):
    """
    DSCOVR 데이터 셋 기본 클래스
    - 추상 클래스 BaseDataset 내용 구현
    """
    def __init__(self, file_):
        super(DscovrDataset, self).__init__(file_)

class DscovrMagDataset(DscovrDataset):
    """
    'dscovr_mag_YYYYMMDD.txt' 파일 데이터 셋 클래스
    - DscovrDataset 클래스 내용 구현
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
        - 파일 내용을 1줄씩 읽어 헤더와 데이터 부분 분류
        - 분류 후 각 정보별 파싱 함수 호출
        """
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = ""
        data = ""
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                header += line + '\n'
            else:
                data += line + '\n'
        self.parsing_header(header.strip())
        self.parsing_data(data.strip())
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
        - 각 줄의 위치별로 날짜+시간, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        lines = data.strip().split('\n')
        for line in lines:
            data_line = line.split()
            str_date = data_line[0] + ' ' + data_line[1]
            del data_line[0]
            del data_line[0]
            data_line.insert(0, str_date)
            for i, value in enumerate(data_line):
                if i == 0:
                    data_line[i] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)
        
        names = [
            'Date',
            'bx_gsm',
            'by_gsm',
            'bz_gsm',
            'lon_gsm',
            'lat_gsm',
            'bt'
        ]
        types = [np.float64 for _ in range(6)]
        types.insert(0, 'datetime64[us]')
        for i in range(len(names)):
            dtype_list.append(tuple((names[i], types[i])))

        dates = np.array([line[0] for line in data_line_list], dtype = 'datetime64[us]')
        values = np.array([line[1:] for line in data_line_list])
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(zip(dates, *values.T)), dtype = dtype)

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
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = [
            'bx_gsm',
            'by_gsm',
            'bz_gsm',
            'lon_gsm',
            'lat_gsm',
            'bt'
        ]

        if show_seperate:
            fig, axs = plt.subplots(2, 3, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 3, i % 3
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                ax.set_xlabel('Date')
                if col == 0:
                    ax.set_ylabel('Value')
                ax.set_title(name)
                ax.grid(True)
                plt.setp(ax.get_xticklabels(), rotation = 45)
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
            plt.title('Dscovr Mag')
            plt.legend()
            plt.grid(True)
            plt.show()

class DscovrPlasmaDataset(DscovrDataset):
    """
    'dscovr_plasma_YYYYMMDD.txt' 파일 데이터 셋 클래스
    - DscovrDataset 클래스 내용 구현
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
        - 파일 내용을 1줄씩 읽어 헤더와 데이터 부분 분류
        - 분류 후 각 정보별 파싱 함수 호출
        """
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = ""
        data = ""
        for line in lines:
            line = line.strip()
            if line.startswith('#'):
                header += line + '\n'
            else:
                data += line + '\n'
        self.parsing_header(header.strip())
        self.parsing_data(data.strip())
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
        - 각 줄의 위치별로 날짜+시간, 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        lines = data.strip().split('\n')
        for line in lines:
            data_line = line.split()
            str_date = data_line[0] + ' ' + data_line[1]
            del data_line[0]
            del data_line[0]
            data_line.insert(0, str_date)
            for i, value in enumerate(data_line):
                if i == 0:
                    data_line[i] = datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
                elif i == 3:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        names = [
            'Date',
            'density',
            'speed',
            'temperature'
        ]
        types = ['datetime64[us]']
        types.append(np.float64)
        types.append(np.float64)
        types.append(np.int64)
        for i in range(len(names)):
            dtype_list.append(tuple((names[i], types[i])))

        dates = np.array([line[0] for line in data_line_list], dtype = 'datetime64[us]')
        values = np.array([line[1:] for line in data_line_list])
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(zip(dates, *values.T)), dtype = dtype)

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
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default 
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['density', 'speed', 'temperature']

        if show_seperate:
            fig, axs = plt.subplots(3, 1, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                ax = axs[i]
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
            plt.title('Dscovr Plasma')
            plt.legend()
            plt.grid(True)
            plt.show()