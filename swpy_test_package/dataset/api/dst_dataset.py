"""
dst_dataset_2.py
"""
# 필요 라이브러리, 모듈 내용 불러오기
from .base_dataset import BaseDataset
import numpy as np
import matplotlib.pyplot as plt
 
class dstDataset(BaseDataset):
    """
    DST 데이터 셋 기본 클래스
    - 추상 클래스 BaseDataset 내용 구현
    """
    def __init__(self, file_):
        """
        생성자 함수
        """
        super(dstDataset, self).__init__(file_)

    def parsing(self):
        """
        전체 데이터 파싱 함수
        - 파일 내용을 1줄씩 읽어 헤더와 데이터 부분 분류
        - 연, 월, 시 데이터 분류, 측정값 하나의 리스트에 병합
        - 분류 후 각 정보별 파싱 함수 호출
        """
        numbers = [] 
        strings = []
        with open(self.file_, 'r') as file:
            for line in file:
                line_data = line.strip().split()
                if line_data:
                    n_data = []
                    s_data = []
                    for value in line_data:
                        try:
                            n_data.append(int(value))
                        except ValueError:
                            s_data.append(value)
                    if n_data:
                        numbers.append(n_data)
                    if s_data:
                        strings.append(s_data)

        DST = np.array(numbers[2:])
        STR = [''.join(row) for row in strings]
        
        MONTH = STR[2] #변수
        YEAR = numbers[0][0] #변수
        HOUR = np.array(numbers[1]) #변수
        
        h = []
        d = []
        for lst in DST:
            f = lst[0]
            h.append(f)

            f_output = lst[1:]
            d.extend(f_output) 
      
        HEADER = np.array(h) #변수
        DATA = np.array(d) #변수
        
        def m(MONTH):
            """
            월 단위 변환 함수
            """
            if MONTH == 'JANUARY':
                month = '01'
                
            elif MONTH == 'FEBRUARY':
                month = '02'
                
            elif MONTH == 'MARCH':
                month = '03'
    
            elif MONTH == 'APRIL':
                month = '04'
    
            elif MONTH == 'MAY':
                month = '05'

            elif MONTH == 'JUNE':
                month = '06'

            elif MONTH == 'JULY':
                month = '07'
    
            elif MONTH == 'AUGUST':
                month = '08'
    
            elif MONTH == 'SEPTEMBER':
                month = '09'
    
            elif MONTH == 'OCTOBER':
                month = '10'
    
            elif MONTH == 'NOVEMBER':
                month = '11'
    
            else:
                month = '12'
    
            return month

        mon = m(MONTH)
        
        YearMon = [f'{YEAR}-{mon}-']
        
        dayhour = []
        for day in HEADER:
            for hour in HOUR:
                dayhour = dayhour + [f'{day:02} {hour:02}:00:00.000']
                
        DayHour = np.array(dayhour)
        
        result = [f'{ym}{dh}'.replace("'","") for ym in YearMon for dh in DayHour]
        Date = np.array(result) # 변수
        
        self.parsing_header(STR)
        self.parsing_data(Date, DATA)
        self.parsing_all(MONTH, YEAR, HOUR, HEADER) 
       
    def parsing_header(self, STR):
        """
        헤더 부분 파싱 함수
        - header에 내용 저장
        """
        self.header = STR
        
    def parsing_data(self, Date, DATA):
        """
        데이터 부분 파싱 함수
        - 데이터별 이름, 타입을 설정하여 Numpy Structured Array로 data에 저장
        """
        data = np.zeros(len(Date), dtype = [('Date', '<U23'), ('Value', int)])
        for i, (date, value) in enumerate(zip(Date, DATA)):
            data[i] = (date, value)
            
        self.data = data
        
    def parsing_all(self, MONTH,YEAR,HOUR,HEADER):
        """
        헤더+데이터 부분 파싱 함수
        - 연, 월, 시, 일, 헤더, 데이터 정보를 딕셔너리 형태로 all에 저장
        """
        self.month = MONTH
        self.year = YEAR
        self.hour = HOUR
        self.day = HEADER
        
        all = {'HEADER' : self.header, 
                'DATA' : self.data, 
                'YEAR' : self.year, 
                'MONTH' : self.month,
                'HOUR' : self.hour, 
                'DAY' : self.day}
        
        self.all = all 
        
class DSTDataset(dstDataset):
    """
    'YYYYMM_dst_obs.txt' 파일 데이터 셋 클래스
    - dstDataset 클래스 내용 구현
    """
    def __init__(self, file_):
        """
        생성자 함수
        """
        super(DSTDataset, self).__init__(file_)
        
    def plot(self):
        """
        데이터 시각화 함수
        - 조회 데이터 구간 입력, 미입력 시 전체 구간 조회
        - 구간에 맞게 데이터 시각화 표시
        """
        start_default = self.data[0][0]
        end_default = self.data[-1][0]
        start = input("Enter the start date (YYYY-MM-DD hh:00:00.000 / None): ") # YYYY-MM-DD hh:00:00.000
        end = input("Enter the end date (YYYY-MM-DD hh:00:00.000 / None): ") # YYYY-MM-DD hh:00:00.000
        index1 = np.where(self.data['Date'] == start)[0] if start != 'None' else np.where(self.data['Date'] == start_default)[0]
        index2 = np.where(self.data['Date'] == end)[0] if end != 'None' else np.where(self.data['Date'] == end_default)[0]

        if len(index1)>0 and len(index2)>0:
            i = index1[0]
            j = index2[0] + 1
    
            interval = self.data['Date'][i : j]

            plt.figure(figsize=(10,6))
        
            plt.plot(interval, self.data['Value'][i : j])
            
            if len(interval)>=6:
                x_ticks = range(0, len(interval), len(interval) // 6)
                
            else:
                x_ticks = range(len(interval))
                
            plt.xticks(x_ticks, rotation=50)
            
            title1 = "WDC for Geomagnetism, Kyoto Hourly Equatorial Dst Values (REAL-TIME)"
            title2 = f"{interval[0]} ~ {interval[-1]}"
            comb_title = f"{title1}\n{title2}"
            
            plt.title(f'{comb_title}')
            plt.ylabel('Dst Value')
            plt.grid()
            plt.tight_layout()
            plt.show()
         
        else:
             print("Value not found in Date")