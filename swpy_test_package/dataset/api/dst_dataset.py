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
        self.header = STR
        
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