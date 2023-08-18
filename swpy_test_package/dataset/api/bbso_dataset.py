# 필요 라이브러리, 모듈 내용 불러오기
from .base_dataset import BaseDataset
from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt


class BBSODataset(BaseDataset):
    """
    BBSO 데이터 셋 기본 클래스
    - 추상 클래스 BaseDataset 내용 구현
    """
    def __init__(self, file_):
        super(BBSODataset, self).__init__(file_)
    #     self.parsing()

class BBSOFtsDataset(BBSODataset):
    """
    'bbso_halph_fl_YYYYMMDD_hhmmss.fts', 'bbso_halph_fr_YYYYMMDD_hhmmss.fts' 파일 데이터 셋 클래스
    - BBSODataset 클래스 내용 구현
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
        - hdu의 헤더 부분을 불러와 딕셔너리 형태로 header에 내용 저장
        """
        hdu = fits.open(self.file_)[-1]
        header = hdu.header
        self.header = dict(header.items())

    def parsing_data(self):
        """
        데이터 부분 파싱 함수
        - hdu의 데이터 부분을 불러와 data에 내용 저장
        """
        hdu = fits.open(self.file_)[-1]
        data = hdu.data
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
        - data와 header의 크기, 수치 정보를 불러와 최대값, 최소값 설정
        - 단위 표시와 함께 data 내용 시각화
        """
        data = self.data
        naxis1 = self.header["NAXIS1"]
        cdelt1 = self.header["CDELT1"]
        naxis2 = self.header["NAXIS2"]
        cdelt2 = self.header["CDELT2"]

        xmin = - naxis1 / 2. * cdelt1
        xmax = naxis1 / 2. * cdelt1
        ymin = - naxis2 / 2. * cdelt2
        ymax = naxis2 / 2. * cdelt2
        vmin, vmax = np.min(data), np.max(data)

        plt.figure()
        plt.imshow(data, vmin=vmin, vmax=vmax, extent = [xmin, xmax, ymin, ymax], cmap="gray")
        plt.title("%s" % (self.header["COMMENT"]))
        plt.xlabel(self.header["CTYPE1"])
        plt.ylabel(self.header["CTYPE2"])
        plt.show()

class BBSOTxtDataset(BBSODataset):
    """
    'bbso_logs_YYYYMMDD.txt' 파일 데이터 셋 클래스
    - BBSODataset 클래스 내용 구현
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
            content = file.read()
            pattern = '+------   H-alpha   ------------------------------------------------------------+'
            header, data = content.split(pattern, 1)
            self.parsing_header(header)
            self.parsing_data(pattern, data)
            self.parsing_all()

    def parsing_header(self, header):
        """
        헤더 부분 파싱 함수
        - header에 내용 저장
        """
        self.header = header.strip()

    def parsing_data(self, pattern, data):
        """
        데이터 부분 파싱 함수
        - data에 내용 저장
        """
        self.data = pattern + '\n' + data.strip()
            
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
        - 시각화할 데이터가 없다고 판단하여 생략
        """
        pass

class BBSOFtsGzDataset(BBSODataset):
    """
    'oact_halph_fl_YYYYMMDD_hhmmss.fts.gz', 'oact_halph_fr_YYYYMMDD_hhmmss.fts.gz' 파일 데이터 셋 클래스
    - BBSODataset 클래스 내용 구현
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
        - hdu의 헤더 부분을 불러와 딕셔너리 형태로 header에 내용 저장
        """
        hdu = fits.open(self.file_)[-1]
        header = hdu.header
        self.header = dict(header.items())

    def parsing_data(self):
        """
        데이터 부분 파싱 함수
        - hdu의 데이터 부분을 불러와 data에 내용 저장
        """
        hdu = fits.open(self.file_)[-1]
        data = hdu.data
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
        - data와 header의 크기 정보를 불러와 최대값, 최소값 설정
        - data 내용 시각화
        """
        data = self.data
        naxis1 = self.header["NAXIS1"]
        naxis2 = self.header["NAXIS2"]

        xmin = - naxis1 / 2.
        xmax = naxis1 / 2.
        ymin = - naxis2 / 2.
        ymax = naxis2 / 2.
        vmin, vmax = np.min(data), np.max(data)

        plt.figure()
        plt.imshow(data, vmin=vmin, vmax=vmax, extent = [xmin, xmax, ymin, ymax], cmap="gray")
        plt.title("%s" % (self.header["COMMENT"]))
        plt.show()