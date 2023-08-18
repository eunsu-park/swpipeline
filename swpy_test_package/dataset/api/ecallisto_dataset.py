# 필요 라이브러리, 모듈 내용 불러오기
from .base_dataset import BaseDataset
from astropy.io import fits
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

class EcallistoDataset(BaseDataset):
    """
    E_Callisto 데이터 셋 기본 클래스
    - 추상 클래스 BaseDataset 내용 구현
    """
    def __init__(self, file_):
        super(EcallistoDataset, self).__init__(file_)
    #     self.parsing()

class EcallistoSpFitDataset(EcallistoDataset):
    """
    'ec_sp_YYYYmmdd_hhmmss_59.fit' 파일 데이터 셋 클래스
    - EcallistoDataset 클래스 내용 구현
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
        - 각 정보별 파싱 함수 호출
        """
        self.parsing_header()
        self.parsing_data()
        self.parsing_all()

    def parsing_header(self):
        """
        헤더 부분 파싱 함수
        - hdu의 헤더 부분들을 불러와 딕셔너리 형태로 header에 내용 저장
        """
        hdu = fits.open(self.file_)
        header1 = hdu[0].header
        header2 = hdu[1].header
        self.header = [dict(header1.items()), dict(header2.items())]

    def parsing_data(self):
        """
        데이터 부분 파싱 함수
        - hdu의 데이터 부분들을 불러와 data에 내용 저장
        """
        hdu = fits.open(self.file_)
        data1 = hdu[0].data
        data2 = hdu[1].data
        self.data = [data1, data2]

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
        - data의 시간과 빈도 값을 불러와 x축, y축으로 설정하여 이미지 생성
        """
        time_data = self.data[1]['TIME'][0]
        frequency_data = self.data[1]['FREQUENCY'][0]

        x = time_data
        y = frequency_data
        data = self.data[0]

        plt.imshow(data, extent=(x.min(), x.max(), y.min(), y.max()), cmap='viridis')
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.title('e-CALLISTO sp 59')
        cbar = plt.colorbar()
        cbar.set_label('Value')
        plt.show()

class EcallistoLPTCSLogDataset(EcallistoDataset):
    """
    'LPTCS_YYYYMMDD.log' 파일 데이터 셋 클래스
    - EcallistoDataset 클래스 내용 구현
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
        header = lines[0]
        data = lines[1:]
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
        for line in data:
            data_line = line.split()
            if len(data_line) == 6:
                str = data_line[0] + data_line[1]
                del data_line[0]
                del data_line[0]
                data_line.insert(0, str)
            data_line[0] = self.file_[-12:-4] + ' ' + data_line[0]
            for i, value in enumerate(data_line):
                if i == 0:
                    data_line[i] = datetime.strptime(value, "%Y%m%d %H:%M:%S")
                else:
                    data_line[i] = int(value)
            data_line_list.append(data_line)

        dates = np.array([line[0] for line in data_line_list], dtype='datetime64[us]')
        values = np.array([line[1:] for line in data_line_list])

        dtype = np.dtype([
            ('Log_Time', 'datetime64[us]'),
            ('Sun_Az', np.int64),
            ('Sun_El', np.int64),
            ('Ant_Az', np.int64),
            ('Ant_El', np.int64)
        ])

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
        - 통합 시각화의 경우 스케일링후 종류별로 색을 통해 분류
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

        filtered_data = self.data[(self.data[names[0]] >= start) * (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = [
            'Sun_Az',
            'Sun_El',
            'Ant_Az',
            'Ant_El'
        ]

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
            plt.title('Ace Mag 1m')
            plt.legend()
            plt.grid(True)
            plt.show()

class EcallistoLPTCSTxtDataset(EcallistoDataset):
    """
    'LPTCS_YYYYMMDD.txt' 파일 데이터 셋 클래스
    - EcallistoDataset 클래스 내용 구현
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
        header = lines[:3]
        data = lines[3:]
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
        - 각 줄의 위치별로 날짜+시간, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        for line in data:
            data_line = line.split()
            data_line[0] = self.file_[-12:-4] + ' ' + data_line[0]
            for i, value in enumerate(data_line):
                if i == 0:
                    data_line[i] = datetime.strptime(value, "%Y%m%d %H:%M:%S")
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        dates = np.array([line[0] for line in data_line_list], dtype='datetime64[us]')
        values = np.array([line[1:] for line in data_line_list])

        dtype = np.dtype([
            ('TIME', 'datetime64[us]'),
            ('SOLAR POSITION Azimuth', np.float64),
            ('SOLAR POSITION Elevation', np.float64),
            ('ANTENNA POSITION Azimuth', np.float64),
            ('ANTENNA POSITION Elevation', np.float64)
        ])

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
            'SOLAR POSITION Azimuth',
            'SOLAR POSITION Elevation',
            'ANTENNA POSITION Azimuth',
            'ANTENNA POSITION Elevation'
        ]

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
            plt.title('Ace Mag 1m')
            plt.legend()
            plt.grid(True)
            plt.show()