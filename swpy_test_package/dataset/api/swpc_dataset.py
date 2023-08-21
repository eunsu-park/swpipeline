# 필요 라이브러리, 모듈 내용 불러오기
from .base_dataset import BaseDataset
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

class SWPCDataset(BaseDataset):
    """
    SWPC 데이터 셋 기본 클래스
    - 추상 클래스 BaseDataset 내용 구현
    """
    def __init__(self, file_):
        super(SWPCDataset, self).__init__(file_)
    #     self.parsing()

class SWPCDSDDataset(SWPCDataset):
    """
    'YYYY_DSD.txt' 파일 데이터 셋 클래스
    - SWPCDataset 클래스 내용 구현
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
            if line.startswith(':') or line.startswith('#'):
                header += line
            else:
                data += line
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
        - 각 줄의 위치별로 날짜+시간, 정수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        lines = [line for line in data.strip().split('\n') if line.strip() != '']
        for line in lines:
            data_line = line.split()
            str_date = data_line[0] + ' ' + data_line[1] + ' ' + data_line[2]
            del data_line[0]
            del data_line[0]
            del data_line[0]
            data_line.insert(0, str_date)
            for i, value in enumerate(data_line):
                if i == 0:
                    data_line[i] = datetime.strptime(value, "%Y %m %d")
                elif i != 6:
                    data_line[i] = int(value)
            data_line_list.append(data_line)
        
        names = [
            'Date',
            'Radio Flux 10.7cm',
            'SESC Sunspot Number',
            'Sunspot Area 10E-6 Hemis.',
            'New Regions',
            'Stanford Solar Mean Field',
            'GOES15 X-Ray Bkgd Flux',
            'X-Ray (C)',
            'X-Ray (M)',
            'X-Ray (X)',
            'X-Ray (S)',
            'Optical (1)',
            'Optical (2)',
            'Optical (3)'
        ]
        types = [np.int64 for _ in range(12)]
        types.insert(0, 'datetime64[us]')
        types.insert(6, 'U20')
        for i in range(len(names)):
            dtype_list.append(tuple((names[i], types[i])))

        dates = np.array([line[0] for line in data_line_list], dtype='datetime64[us]')
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
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = list(names[1:])
        del values_name[5]

        if show_seperate:
            fig, axs = plt.subplots(3, 4, figsize = (10, 10), gridspec_kw = {'hspace':0.8})
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
            plt.title('SWPC DSD')
            plt.legend()
            plt.grid(True)
            plt.show()

class SWPCDayobsDataset(SWPCDataset):
    """
    'YYYYMMDDdayobs.txt' 파일 데이터 셋 클래스
    - SWPCDataset 클래스 내용 구현
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
            if line.startswith(':') or line.startswith('#'):
                header += line
            else:
                data += line
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
        - 각 줄의 내용을 분리하여 data에 저장
        """
        lines = [line for line in data.strip().split('\n') if line.strip() != '']
        rows = [line.split() for line in lines]
        self.data = np.array(rows)
            
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
        - 시각화 가능한 데이터가 아니라고 판단하여 생략
        """
        pass

class SWPCDaypreDataset(SWPCDataset):
    """
    'YYYYMMDDdaypre.txt' 파일 데이터 셋 클래스
    - SWPCDataset 클래스 내용 구현
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
            if line.startswith(':') or line.startswith('#'):
                header += line
            else:
                data += line
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
        - data에 내용 저장
        """
        self.data = data
            
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
        - 시각화 가능한 데이터가 아니라고 판단하여 생략
        """
        pass

class SWPCRSGADataset(SWPCDataset):
    """
    'YYYYMMDDRSGA.txt' 파일 데이터 셋 클래스
    - SWPCDataset 클래스 내용 구현
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
            if line.startswith(':') or line.startswith('#'):
                header += line
            else:
                data += line
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
        - data에 내용 저장
        """
        self.data = data
            
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
        - 시각화 가능한 데이터가 아니라고 판단하여 생략
        """
        pass

class SWPCSGASDataset(SWPCDataset):
    """
    'YYYYMMDDSGAS.txt' 파일 데이터 셋 클래스
    - SWPCDataset 클래스 내용 구현
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
            if line.startswith(':') or line.startswith('#'):
                header += line
            else:
                data += line
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
        - data에 내용 저장
        """
        self.data = data
            
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
        - 시각화 가능한 데이터가 아니라고 판단하여 생략
        """
        pass

class SWPCSRSDataset(SWPCDataset):
    """
    YYYYMMDDSRS.txt' 파일 데이터 셋 클래스
    - SWPCDataset 클래스 내용 구현
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
            if line.startswith(':') or line.startswith('#'):
                header += line
            else:
                data += line
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
        - data에 내용 저장
        """
        self.data = data
            
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
        - 시각화 가능한 데이터가 아니라고 판단하여 생략
        """
        pass

class SWPCAuroraPowerDataset(SWPCDataset):
    """
    'swpc_aurora_power_YYYYMMDD.txt' 파일 데이터 셋 클래스
    - SWPCDataset 클래스 내용 구현
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
            if line.startswith('#'):
                header += line
            else:
                data += line
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
        - 각 줄의 위치별로 날짜+시간, 정수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        dtype_list = []
        dates = []
        values = []
        data_list = data.strip().split('\n')
        for data_line in data_list:
            date_list = []
            index_list = []
            data_line_list = data_line.split()
            date_obs = data_line_list[0]
            date_for = data_line_list[1]
            index_north = data_line_list[2]
            index_south = data_line_list[3]
            date_list.append(datetime.strptime(date_obs, "%Y-%m-%d_%H:%M"))
            date_list.append(datetime.strptime(date_for, "%Y-%m-%d_%H:%M"))
            index_list.append(int(index_north))
            index_list.append(int(index_south))
            dates.append(date_list)
            values.append(index_list)
        
        names = [
            'Observation Date',
            'Forecast Date',
            'North-Hemispheric_Power-Index-GigaWatts',
            'South-Hemispheric_Power-Index-GigaWatts'
        ]
        types = [
            'datetime64[us]',
            'datetime64[us]',
            np.int64,
            np.int64
        ]
        for i in range(len(names)):
            dtype_list.append(tuple((names[i], types[i])))

        dates = np.array(dates, dtype = 'datetime64[us]')
        values = np.array(values)
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(zip(*dates.T, *values.T)), dtype = dtype)
            
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
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = []
        indices = []
        dates.append(filtered_data[names[0]])
        dates.append(filtered_data[names[1]])
        indices.append(filtered_data[names[2]])
        indices.append(filtered_data[names[3]])

        if show_seperate:
            fig, axs = plt.subplots(2, 2, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, date in enumerate(dates):
                for j, index in enumerate(indices):
                    ax = axs[i, j]
                    ax.plot(date, index, label = names[i + 2] + ' (' + names[j].split()[0] + ')')
                    ax.set_xlabel('Date')
                    ax.set_ylabel('Value')
                    ax.set_title(names[i + 2] + ' (' + names[j].split()[0] + ')')
                    ax.grid(True)
                    plt.setp(ax.get_xticklabels(), rotation = 45)
            plt.tight_layout()
            plt.show()
        else:
            for i, date in enumerate(dates):
                for j, index in enumerate(indices):
                    plt.plot(date, index, label = names[i + 2] + ' (' + names[j].split()[0] + ')')
            plt.xlabel('Date')
            plt.ylabel('Index')
            plt.title('SWPC Aurora Power')
            plt.legend()
            plt.grid(True)
            plt.show()