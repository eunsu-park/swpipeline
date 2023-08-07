from .base_dataset import BaseDataset
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

class JbsDataset(BaseDataset):
    def __init__(self, file_):
        super(JbsDataset, self).__init__(file_)

class JbsIonoDataset(JbsDataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None
    
    def parsing(self):
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        self.header = header

    def parsing_data(self, data):
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()
            for i, value in enumerate(data_line):
                if i == 0 or i == 1 or i == 5:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)
        
        for i in range(len(data_line_list[0])):
            if i ==0 or i == 1 or i == 5:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64)))
        
        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        names = self.data.dtype.names
        start_default = self.data[names[1]][0]
        end_default = self.data[names[1]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[1]] >= start) & (self.data[names[1]] <= end)]
        dates = filtered_data[names[1]]
        values_name = [
            'Col3',
            'Col4',
            'Col5',
            'Col6'
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
            plt.title('Jbs Scint Iono')
            plt.legend()
            plt.grid(True)
            plt.show()

class JbsNavsolDataset(JbsDataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        self.header = header

    def parsing_data(self, data):
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()
            for i, value in enumerate(data_line):
                if i == 0 or i == 1 or i == 11:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i == 0 or i == 1 or i == 11:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64)))
        
        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        names = self.data.dtype.names
        start_default = self.data[names[1]][0]
        end_default = self.data[names[1]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[1]] >= start) & (self.data[names[1]] <= end)]
        dates = filtered_data[names[1]]
        values_name = ['Col' + str(i) for i in range(3, 13)]

        if show_seperate:
            fig, axs = plt.subplots(5, 2, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 2, i % 2
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                if row == 4:
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
            plt.title('Jbs Scint Navsol')
            plt.legend()
            plt.grid(True)
            plt.show()

class JbsScintDataset(JbsDataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        self.header = header

    def parsing_data(self, data):
        data_line_list = []
        dtype_list = []
        int_index = [0, 1, 12, 13, 14]
        for line in data:
            data_line = line.strip().split()
            for i, value in enumerate(data_line):
                if i in int_index:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i in int_index:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64))) 
        
        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        names = self.data.dtype.names
        start_default = self.data[names[1]][0]
        end_default = self.data[names[1]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[1]] >= start) & (self.data[names[1]] <= end)]
        dates = filtered_data[names[1]]
        values_name = ['Col' + str(i) for i in range(3, 16)]
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
            plt.title('Jbs Scint Scint')
            plt.legend()
            plt.grid(True)
            plt.show()

class JbsTxinfoDataset(JbsDataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = None
        data = lines
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        self.header = header
    
    def parsing_data(self, data):
        data_line_list = []
        dtype_list = []
        int_index = [0, 1, 5, 6, 7]
        for line in data:
            data_line = line.strip().split()
            for i, value in enumerate(data_line):
                if i in int_index:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i in int_index:
                dtype_list.append(tuple(('Col' + str(i + 1), np.uint64)))
            else:
                dtype_list.append(tuple(('Col' + str(i + 1), np.float64)))
        
        values = list(map(tuple, data_line_list))
        dtype = np.dtype(dtype_list)
        self.data = np.array(list(values), dtype = dtype)

    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

    def plot(self):
        names = self.data.dtype.names
        start_default = self.data[names[1]][0]
        end_default = self.data[names[1]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[1]] >= start) & (self.data[names[1]] <= end)]
        dates = filtered_data[names[1]]
        values_name = ['Col' + str(i) for i in range(3, 9)]

        if show_seperate:
            fig, axs = plt.subplots(3, 2, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
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
            plt.title('Jbs Scint Txinfo')
            plt.legend()
            plt.grid(True)
            plt.show()