# 필요 라이브러리, 모듈 내용 불러오기
from .base_dataset import BaseDataset
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

class MagnetometerDataset(BaseDataset):
    """
    Magnetometer 데이터 셋 기본 클래스
    - 추상 클래스 BaseDataset 내용 구현
    """
    def __init__(self, file_):
        super(MagnetometerDataset, self).__init__(file_)
    #     self.parsing()

class MagnetometerBOHminDataset(MagnetometerDataset):
    """
    'gm_boh_min_YYYYMMDD.txt' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
        - 헤더가 존재하지 않아 데이터 부분만 분류
        - 분류 후 각 정보별 파싱 함수 호출
        """
        with open(self.file_, "r") as file:
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
        - 각 줄의 위치별로 날짜+시간, 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split(',')
            data_line[0] = self.file_[-12:-10] + data_line[0]
            for i,value in enumerate(data_line):
                if i == 0:
                    data_line[i] = datetime.strptime(value, "%Y/%m/%d %H:%M:%S")
                elif i == 9 or i == 13 or i == 14:
                    data_line[i] = value.strip()
                elif i == 7 or i == 15:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i, value in enumerate(data_line):
            col = 'Col' + str(i + 1)
            if i == 0:
                dtype_list.append(tuple((col, 'datetime64[us]')))
            elif i == 9 or i == 13 or i == 14:
                dtype_list.append(tuple((col, 'U20')))
            elif i == 7 or i == 15:
                dtype_list.append(tuple((col, np.int64)))
            else:
                dtype_list.append(tuple((col, np.float64)))

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
        values_name = names[1:7]

        if show_seperate:
            fig, axs = plt.subplots(3, 2, figsize = (10, 10), gridspec_kw = {'hspace':0.8})
            for i, name in enumerate(values_name):
                row, col = i // 2, i % 2
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
            plt.title('GM BOH min')
            plt.legend()
            plt.grid(True)
            plt.show()

class MagnetometerBOHsec5Dataset(MagnetometerDataset):
    """
    'gm_boh_sec5_YYYYMMDD.txt' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
        with open(self.file_, "r") as file:
            lines = file.readlines()
        header = lines[0]
        data = [line.split() for line in lines[1:]]
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
        - 'doy'는 불필요하다 판단해 데이터에서 제외 -> 헤더 뒤에 추가
        - 각 줄의 위치별로 날짜+시간, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        dtype_list = []
        dates = []
        values = []
        doy = data[0][3]
        self.header = self.header[:-1] + ' doy:' + str(doy)
        for line in data:
            date_str = ' '.join(line[:3]) + ' ' + ' '.join(line[4:7])
            data_num = ' '.join(line[7:])
            data_num_list = [float(value) for value in data_num.split()]
            date = datetime.strptime(date_str, "%Y %m %d %H %M %S")
            dates.append(date)
            values.append(data_num_list)

        names = ['Date', 'H [nT]', 'D [nT]', 'Z [nT]', 'Proton [nT]']
        types = ['datetime64[us]', np.float64, np.float64, np.float64, np.float64]
        dtype_list = list(zip(names, types))

        dates = np.array(dates, dtype = 'datetime64[us]')
        values = np.array(values)
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
        - 개별 시각화의 경우, 종류별로 분할
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
        values_name = names[1:]

        if show_seperate:
            fig, axs = plt.subplots(2, 2, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 2, i % 2
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                if row == 1:
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
            plt.title('GM BOH sec5')
            plt.legend()
            plt.grid(True)
            plt.show()

class MagnetometerKindexDataset(MagnetometerDataset):
    """
    'kindex_YYYYMM.txt' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
            header = ""
            data = ""
            for line in file:
                line = line.strip()
                if line.startswith(':') or line.startswith('#'):
                    header += line + "\n"
                else:
                    data += line + "\n"
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
        - 각 줄의 내용이 날짜별로 8개의 시간대로 기록되어 통합되게 변환
        - 각 줄의 위치별로 날짜+시간, 정수형 데이터로 변환
        - 변환 후 data에 저장
        """
        hours = ['00', '03', '06', '09', '12', '15', '18', '21']
        values = []
        lines = data.strip().split("\n")
        lines = [line for line in lines if line.strip() != '']
        for line in lines:
            line = line.split() 
            indices = line[3:]
            for i, hour in enumerate(hours):
                data_list = []
                str_date = line[0] + line[1] + line[2]  + ' ' + hour
                date = datetime.strptime(str_date, "%Y%m%d %H")
                data_list.append(date)
                data_list.append(int(indices[i]))
                values.append(data_list)
        values = np.array(values)
        dates = values[:, 0].astype('datetime64')
        values[:, 0] = dates + np.timedelta64(3, 'h')
        self.data = values
            
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
        - 조회 데이터 구간 내의 측정값 그래프로 표시
        """
        names = self.data.dtype.names
        start_default = self.data[0, 0]
        end_default = self.data[-1, 0]
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default

        filtered_data = self.data[(self.data[:, 0] >= start) & (self.data[:, 0] <= end)]
        dates = filtered_data[:, 0]
        values = filtered_data[:, 1]
        x = np.arange(len(values))
        baseline = 0
        colors = np.where(np.array(values) < baseline, 'k', np.where(values < 4, 'g', np.where(values < 7, 'y', 'r')))
        
        plt.bar(x, values, align = 'center', color = colors)
        plt.axhline(y = baseline, color = 'black', linewidth = 0.8)
        plt.ylim(-1, 9)
        plt.xticks(np.arange(len(dates))[::8], dates[::8], rotation = 90)
        plt.xlabel('Date')
        plt.ylabel('K Index')
        plt.title('Geomagnetic K Indices')
        plt.tight_layout()
        plt.show()

class MagnetometerBOHmilDataset(MagnetometerDataset):
    """
    'mi_boh_mil_YYYYMMDD.txt' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
        with open(self.file_, "r") as file:
            lines = file.readlines()
        header = lines[0]
        data = [line.split() for line in lines[1:]]
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
        dtype_list = []
        dates = []
        values = []
        for line in data:
            date_str = ' '.join(line[:4])
            data_num = ' '.join(line[4:])
            data_num_list = []
            for i, value in enumerate(data_num.split()):
                data_num_list.append(float(value))
            date = datetime.strptime(date_str, "%Y %m %d %H:%M:%S.%f")
            dates.append(date)
            values.append(data_num_list)

        names = ['Date', 'X [nT]', 'Y [nT]', 'Z [nT]']
        types = ['datetime64[us]', np.float64, np.float64, np.float64]
        dtype_list = list(zip(names, types))

        dates = np.array(dates, dtype='datetime64[us]')
        values = np.array(values)
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
        values_name = names[1:]

        if show_seperate:
            fig, axs = plt.subplots(3, 1, figsize = (10, 10), gridspec_kw = {'hspace':1.0})
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
            plt.title('MI BOH mil')
            plt.legend()
            plt.grid(True)
            plt.show()

class MagnetometerMISpectrumXDataset(MagnetometerDataset):
    """
    'mi_spectrum_YYYYMMDD_x.txt' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
        with open(self.file_, "r") as file:
            lines = file.readlines()
        header = lines[0]
        data = [line.split() for line in lines[2::2]]
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
        dtype_list = []
        dates = []
        values = []
        for line in data:
            date_str = ' '.join(line[:4])
            data_num = ' '.join(line[4:])
            data_num_list = []
            for i, value in enumerate(data_num.split()):
                data_num_list.append(float(value))
            date = datetime.strptime(date_str, "%Y %m %d %H:%M:%S")
            dates.append(date)
            values.append(data_num_list)

        names = ['Time']
        count_dict = {}
        for name in self.header.split()[6:]:
            if name in count_dict:
                count_dict[name] += 1
                names.append(name + str(count_dict[name]))
            else:
                count_dict[name] = 0
                names.append(name)
        types = [np.float64 for _ in range(len(names))]
        types.insert(0, 'datetime64[us]')
        dtype_list = list(zip(names, types))

        dates = np.array(dates, dtype='datetime64[us]')
        values = np.array(values)
        dtype = np.dtype(dtype_list)
        data_list = np.array(list(zip(dates, *values.T)))
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
        - x축을 측정 날짜, y축을 측정값 종류로 하여 이미지 생성
        - 각 측정값에 따라 색을 통해 분류하여 표시
        """
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        features = names[1:]
        values = np.column_stack([filtered_data[name] for name in features])
        scaled_values = (values - np.min(values)) / (np.max(values) - np.min(values))
        scaled_values = scaled_values.T

        fig, ax = plt.subplots()
        im = ax.imshow(scaled_values, aspect = 'auto', cmap = 'viridis')
        num_dates = len(dates)
        ax.set_xticks(range(0, num_dates, num_dates // 6))
        ax.set_xticklabels(dates[::num_dates // 6], rotation = 45)
        ax.set_yticks(range(0, len(features), 60))
        ax.set_yticklabels(features[::60])
        cbar = ax.figure.colorbar(im, ax = ax)
        cbar.set_label('Value (Min-Max Scaling)')
        plt.title('MI Spectrum X')
        plt.tight_layout()
        plt.show()

class MagnetometerMISpectrumYDataset(MagnetometerDataset):
    """
    'mi_spectrum_YYYYMMDD_y.txt' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
        with open(self.file_, "r") as file:
            lines = file.readlines()
        header = lines[0]
        data = lines[2].split()
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
        data_list = []
        year = data[0]
        for i in range(719):
            n = 604 * (i + 1)
            data.insert(n, year)
            data_str = data[n - 1].replace(year, '') 
            del data[n-1]
            data.insert(n-1, data_str)
            data_list.append(data[n- 604:n])
        data_list.append(data[604 * 719:])

        dtype_list = []
        dates = []
        values = []
        for line in data_list:
            date_str = ' '.join(line[:4])
            data_num = ' '.join(line[4:])
            data_num_list = []
            for i, value in enumerate(data_num.split()):
                data_num_list.append(float(value))
            date = datetime.strptime(date_str, "%Y %m %d %H:%M:%S")
            dates.append(date)
            values.append(data_num_list)

        names = ['Time']
        count_dict = {}
        for name in self.header.split()[6:]:
            if name in count_dict:
                count_dict[name] += 1
                names.append(name + str(count_dict[name]))
            else:
                count_dict[name] = 0
                names.append(name)
        types = [np.float64 for _ in range(len(names))]
        types.insert(0, 'datetime64[us]')
        dtype_list = list(zip(names, types))

        dates = np.array(dates, dtype='datetime64[us]')
        values = np.array(values)
        dtype = np.dtype(dtype_list)
        data_list = np.array(list(zip(dates, *values.T)))
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
        - x축을 측정 날짜, y축을 측정값 종류로 하여 이미지 생성
        - 각 측정값에 따라 색을 통해 분류하여 표시
        """
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        features = names[1:]
        values = np.column_stack([filtered_data[name] for name in features])
        scaled_values = (values - np.min(values)) / (np.max(values) - np.min(values))
        scaled_values = scaled_values.T

        fig, ax = plt.subplots()
        im = ax.imshow(scaled_values, aspect = 'auto', cmap = 'viridis')
        num_dates = len(dates)
        ax.set_xticks(range(0, num_dates, num_dates // 6))
        ax.set_xticklabels(dates[::num_dates // 6], rotation = 45)
        ax.set_yticks(range(0, len(features), 60))
        ax.set_yticklabels(features[::60])
        cbar = ax.figure.colorbar(im, ax = ax)
        cbar.set_label('Value (Min-Max Scaling)')
        plt.title('MI Spectrum Y')
        plt.tight_layout()
        plt.show()

class MagnetometerMISpectrumZDataset(MagnetometerDataset):
    """
    'mi_spectrum_YYYYMMDD_z.txt' 파일 데이터 셋 클래스
    - Magnetometer 클래스 내용 구현
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
        with open(self.file_, "r") as file:
            lines = file.readlines()
        header = lines[0]
        data = lines[2].split()
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
        - 각 줄의 위치별로 날짜+시간, 실수형 데이터로 변환 및 결측치 처리
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_list = []
        year = data[0]
        for i in range(719):
            n = 604 * (i + 1)
            data.insert(n, year)
            data_str = data[n - 1].replace(year, '') 
            del data[n-1]
            data.insert(n-1, data_str)
            data_list.append(data[n- 604:n])
        data_list.append(data[604 * 719:])

        dtype_list = []
        dates = []
        values = []
        for line in data_list:
            date_str = ' '.join(line[:4])
            data_num = ' '.join(line[4:])
            data_num_list = []
            for i, value in enumerate(data_num.split()):
                data_num_list.append(float(value))
            date = datetime.strptime(date_str, "%Y %m %d %H:%M:%S")
            dates.append(date)
            values.append(data_num_list)

        names = ['Time']
        count_dict = {}
        for name in self.header.split()[6:]:
            if name in count_dict:
                count_dict[name] += 1
                names.append(name + str(count_dict[name]))
            else:
                count_dict[name] = 0
                names.append(name)
        types = [np.float64 for _ in range(len(names))]
        types.insert(0, 'datetime64[us]')
        dtype_list = list(zip(names, types))

        dates = np.array(dates, dtype='datetime64[us]')
        values = np.array(values)
        dtype = np.dtype(dtype_list)
        data_list = np.array(list(zip(dates, *values.T)))
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
        - x축을 측정 날짜, y축을 측정값 종류로 하여 이미지 생성
        - 각 측정값에 따라 색을 통해 분류하여 표시
        """
        names = self.data.dtype.names
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        features = names[1:]
        values = np.column_stack([filtered_data[name] for name in features])
        scaled_values = (values - np.min(values)) / (np.max(values) - np.min(values))
        scaled_values = scaled_values.T

        fig, ax = plt.subplots()
        im = ax.imshow(scaled_values, aspect = 'auto', cmap = 'viridis')
        num_dates = len(dates)
        ax.set_xticks(range(0, num_dates, num_dates // 6))
        ax.set_xticklabels(dates[::num_dates // 6], rotation = 45)
        ax.set_yticks(range(0, len(features), 60))
        ax.set_yticklabels(features[::60])
        cbar = ax.figure.colorbar(im, ax = ax)
        cbar.set_label('Value (Min-Max Scaling)')
        plt.title('MI Spectrum Z')
        plt.tight_layout()
        plt.show()

class MagnetometerMinAverageDataset(MagnetometerDataset):
    """
    'min_average_YYYYMM.txt' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
        with open(self.file_, "r") as file:
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
        - 각 줄의 위치별로 날짜+시간, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()
            data_line[0] = self.file_[-10:-8] + data_line[0] + ' ' + data_line[1]
            del data_line[1]
            for i, value in enumerate(data_line):
                if i == 0:
                    data_line[i] = datetime.strptime(value, "%Y/%m/%d %H:%M:%S")
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i, value in enumerate(data_line):
            col = 'Col' + str(i + 1)
            if i == 0:
                dtype_list.append(tuple((col, 'datetime64[us]')))
            else:
                dtype_list.append(tuple((col, np.float64)))

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
        values_name = names[1:]

        if show_seperate:
            fig, axs = plt.subplots(2, 1, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
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
            plt.title('min Average')
            plt.legend()
            plt.grid(True)
            plt.show()

class MagnetometerPi2listDataset(MagnetometerDataset):
    """
    'pi2_list_YYYYMMDD.dat' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
        with open(self.file_, "r") as file:
            lines = file.readlines()
        header = lines[0]
        data = [line.split() for line in lines[1:]]
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
        - 각 줄의 위치별로 날짜+시간, 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        dtype_list = []
        dates = []
        values = []
        for line in data:
            date_str = ' '.join(line[0:3]) + ' ' + ' '.join(line[4:7])
            data_num = line[3] + ' ' + ' '.join(line[7:])
            data_num_list = []
            for i, value in enumerate(data_num.split()):
                if i == 3:
                    data_num_list.append(float(value))
                else:
                    data_num_list.append(int(value))
            date = datetime.strptime(date_str, "%Y %m %d %H %M %S.%f")
            dates.append(date)
            values.append(data_num_list)

        names = ['Date', 'pH']
        types = ['datetime64[us]', np.float64]
        dtype_list = list(zip(names, types))

        dates = np.array(dates, dtype='datetime64[us]')
        values = np.array(values)
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(zip(dates, values[:, -1])))
            
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
        - 조회 데이터 구간 내 측정값 그래프로 표시
        """
        start_default = self.data[:, 0][0]
        end_default = self.data[:, 0][-1]
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default

        filtered_data = self.data[(self.data[:, 0] >= start) & (self.data[:, 0] <= end)]
        plt.plot(filtered_data[:, 0], filtered_data[:, -1])
        plt.xlabel('Date')
        plt.ylabel('pH')
        plt.title('PI2 List')
        plt.grid(True)
        plt.show()

class MagnetometerPi2powerDataset(MagnetometerDataset):
    """
    'pi2_power_YYYYMMDD.dat' 파일 데이터 셋 클래스
    - MagnetometerDataset 클래스 내용 구현
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
        with open(self.file_, "r") as file:
            lines = file.readlines()
        header = lines[0]
        data = [line.split() for line in lines[1:]]
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
        - 각 줄의 위치별로 날짜+시간, 정수형, 실수형 데이터로 변환
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        dtype_list = []
        dates = []
        values = []
        for line in data:
            date_str = self.file_[-12:-10] + ' '.join(line[0:3]) + ' ' + ' '.join(line[4:7])
            data_num = line[3] + ' ' + line[7]
            data_num_list = []
            for i, value in enumerate(data_num.split()):
                if i == 0:
                    data_num_list.append(int(value))
                else:
                    data_num_list.append(float(value))
            date = datetime.strptime(date_str, "%Y %m %d %H %M %S.%f")
            dates.append(date)
            values.append(data_num_list)

        names = ['Date', 'Power']
        types = ['datetime64[us]', np.float64]
        dtype_list = list(zip(names, types))

        dates = np.array(dates, dtype='datetime64[us]')
        values = np.array(values)
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(zip(dates, values[:, -1])))
            
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
        - 조회 데이터 구간 내 측정값 그래프로 표시
        """
        start_default = self.data[:, 0][0]
        end_default = self.data[:, 0][-1]
        start_input = input("Enter the start date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        end_input = input("Enter the end date (YYYY-MM-DD HH:MM:SS.ffffff / None): ")
        start = np.datetime64(start_input) if start_input != 'None' else start_default
        end = np.datetime64(end_input) if end_input != 'None' else end_default

        filtered_data = self.data[(self.data[:, 0] >= start) & (self.data[:, 0] <= end)]
        plt.plot(filtered_data[:, 0], filtered_data[:, -1])
        plt.xlabel('Date')
        plt.ylabel('power')
        plt.title('PI2 Power')
        plt.grid(True)
        plt.show()