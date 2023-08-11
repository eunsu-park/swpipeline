"""
dst_dataset_2.py
"""
from .base_dataset import BaseDataset
import numpy as np
import matplotlib.pyplot as plt
 
class dstDataset(BaseDataset):
    def __init__(self, file_):
        super(dstDataset, self).__init__(file_)

    def parsing(self):
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

        DST = np.array(numbers)
        STR = np.array(strings)
        STR_ = [''.join(row) for row in STR]
        
        MONTH = STR[2][0] #변수
        YEAR = DST[0][0] #변수
        
        a = DST[1]
        HOUR = np.array(a) #변수
        
        h = []
        d = []
        for lst in DST[2:]:
            f = lst[0]
            h.append(f)

            f_output = lst[1:]
            d = d + f_output 
      
        HEADER = np.array(h) #변수
        DATA = np.array(d) #변수
        
        def m(Month):
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
        
        self.parsing_header(STR_)
        self.parsing_data(Date, DATA)
        self.parsing_all(MONTH, YEAR, HOUR, HEADER) 
       
    def parsing_header(self, STR_):
        self.header = STR_
        
    def parsing_data(self, Date, DATA):
        data = np.zeros(len(Date), dtype = [('Date', '<U23'), ('Value', int)])
        for i, (date, value) in enumerate(zip(Date, DATA)):
            data[i] = (date, value)
            
        self.data = data
        
    def parsing_all(self, MONTH,YEAR,HOUR,HEADER):
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
    def __init__(self, file_):
        super(DSTDataset, self).__init__(file_)
        
    def plot(self):
        start = input("start (YYYY-MM-DD hh:00:00.000)\n: ") # YYYY-MM-DD hh:00:00.000
        end = input("end (YYYY-MM-DD hh:00:00.000)\n: ") # YYYY-MM-DD hh:00:00.000

        index1 = np.where(self.data['Date'] == start)[0]
        index2 = np.where(self.data['Date'] == end)[0]
    
        if len(index1)>0 and len(index2)>0:
            s_index = index1[0]
            e_index = index2[0]
    
            interval = self.data['Date'][s_index:e_index+1]
    
            i = s_index
            j = e_index+1

            plt.figure(figsize=(10,6))
        
            plt.plot(interval, self.data['Value'][i:j])
            
            if len(interval)>=6:
                x_ticks = range(0, len(interval), len(interval)//6)
                
            else:
                x_ticks = range(len(interval))
                
            plt.xticks(x_ticks, rotation=50)
            
            title1 = "WDC for Geomagnetism, Kyoto Hourly Equatorial Dst Values (REAL-TIME)"
            title2 = f"{interval[0]} ~ {interval[-1]}"
            comb_title = f"{title1}\n{title2}"
            
            plt.title(f'{comb_title}')
            plt.grid()
         
        else:
             print("Value not found in Date")