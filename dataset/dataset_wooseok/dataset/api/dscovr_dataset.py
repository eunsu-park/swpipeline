from .base_dataset import BaseDataset
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

class DscovrDataset(BaseDataset):
    def __init__(self, file_):
        super(DscovrDataset, self).__init__(file_)

class DscovrMagDataset(DscovrDataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
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
        self.header = header

    def parsing_data(self, data):
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
        all = [self.header, self.data]
        self.all = all

    def plot(self):
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
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None
    
    def parsing(self):
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
        self.header = header

    def parsing_data(self, data):
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
        all = [self.header, self.data]
        self.all = all

    def plot(self):
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