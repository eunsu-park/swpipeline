# -*- coding: utf-8 -*-
"""
gye_dataset_log.py
"""
from .base_dataset import BaseDataset
import numpy as np
import matplotlib.pyplot as plt

# 파일 이름 선언해주기 / 파일이 너무 많을 때 메모리에서 지우는게 필요할까?
# class gyeDataset(BaseDataset):
#     def __init__(self, file_):
#         super(gyeDataset, self).__init__(file_)
#         self.file_name = file_
        
#     def parsing(self):
#         with open(self.file_, 'r') as file:
#             d = []
#             count = 0
#             for line in file:
#                 data = line.strip().split('\t')
#                 d = d+data
                
#                 count += 1
#                 if count == 100000:
#                     break
                
#             columns = list(zip(*[line.split() for line in d]))
#             column = np.array(columns)
            
#             dic = {f'column{i+1}': column for i,column in enumerate(column)}
                            
#             HEADER = list(dic.keys())
#             DATA = list(dic.values())
#             ITEM = list(dic.items())
            
#         self.parsing_header(HEADER)
#         self.parsing_data(DATA)
#         self.parsing_all(ITEM)
        
#     def parsing_header(self, HEADER):
#         header = np.array(HEADER)
#         self.header = header
         
#     def parsing_data(self, DATA):
#         data = np.array(DATA)
#         self.data = data
        
#     def parsing_all(self, ITEM):
#         self.item = ITEM
        
#         all = {'HEADER' : self.header,
#                'DATA' : self.data }
        
#         self.all = all

# class GYEDataset(gyeDataset):
#     def __init__(self, file_):
#         super(GYEDataset, self).__init__(file_)
        
#     def plot(self):
#         for i in range(len(self.item)):
#             plt.figure(figsize=(9,6))
#             c_lst = ['b','c','g','r']
#             color_lst = c_lst*4
#             plt.plot(self.item[i][1], label = self.header[i], color = color_lst[i])
            
#             desired_y_ticks = 6

#             y_min, y_max = plt.ylim()
#             num_y_ticks = min(desired_y_ticks, int(y_max - y_min) + 1)
            
#             y_ticks = np.linspace(y_min, y_max, num_y_ticks)
#             plt.yticks(y_ticks,['%.2f' % tick for tick in y_ticks])
            
#             plt.title(f'{self.file_name}')
#             plt.legend(loc = 'upper left', fontsize = 12)

class GyeDataset(BaseDataset):
    def __init__(self, file_):
        super(GyeDataset, self).__init__(file_)

class GyeChannelDataset(GyeDataset):
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
        float_index = [0, 3, 4, 5, 6, 7]
        data_line_list = []
        dtype_list = []
        for line in data:
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i not in float_index:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i not in float_index:
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
        start_default = self.data[names[2]][0]
        end_default = self.data[names[2]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[2]] >= start) & (self.data[names[2]] <= end)]
        dates = filtered_data[names[2]]
        values_name = ['Col1', 'Col2'] + ['Col' + str(i) for i in range(4, 14)]

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
            plt.title('Gye Scint Channel')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()

class GyeIonoDataset(GyeDataset):
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
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i == 0 or i == 4:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)
        
        for i in range(len(data_line_list[0])):
            if i == 0 or i == 4:
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
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[1]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['Col' + str(i) for i in range(2, 6)]

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
            plt.title('Gye Scint Iono')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()

class GyeNavsolDataset(GyeDataset):
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
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i == 0 or i == 10:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)
        
        for i in range(len(data_line_list[0])):
            if i == 0 or i == 10:
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
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['Col' + str(i) for i in range(2, 12)]

        if show_seperate:
            fig, axs = plt.subplots(5, 2, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 2, i % 2
                ax = axs[row, col]
                values = filtered_data[name]
                ax.plot(dates, values, label = name)
                if row == 4:
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
            plt.title('Gye Scint Navsol')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()

class GyeScintDataset(GyeDataset):
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
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i == 0 or i == 11 or i == 12 or i == 13:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i == 0 or i == 11 or i == 12 or i == 13:
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
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['Col' + str(i) for i in range(2, 15)]
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
            plt.title('Gye Scint Scint')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()

class GyeTxinfoDataset(GyeDataset):
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
            data_line = line.strip().split()[1:]
            for i, value in enumerate(data_line):
                if i not in [1, 2, 3]:
                    data_line[i] = int(value)
                else:
                    data_line[i] = float(value)
            data_line_list.append(data_line)

        for i in range(len(data_line_list[0])):
            if i not in [1, 2, 3]:
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
        start_default = self.data[names[0]][0]
        end_default = self.data[names[0]][-1]
        start_input = input(f"Enter the start date ({start_default} ~ {end_default} / None): ")
        end_input = input(f"Enter the end date ({start_default} ~ {end_default} / None): ")
        show_input = input("Enter to show graph seperately (T / F): ")
        start = int(start_input) if start_input != 'None' else start_default
        end = int(end_input) if end_input != 'None' else end_default
        show_seperate = True if show_input == 'T' else False

        filtered_data = self.data[(self.data[names[0]] >= start) & (self.data[names[0]] <= end)]
        dates = filtered_data[names[0]]
        values_name = ['Col' + str(i) for i in range(2, 8)]

        if show_seperate:
            fig, axs = plt.subplots(2, 3, figsize = (10, 10), gridspec_kw = {'hspace':0.5})
            for i, name in enumerate(values_name):
                row, col = i // 3, i % 3
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
            plt.title('Gye Scint Txinfo')
            plt.legend(loc = 'upper left', bbox_to_anchor = (1.0, 1.0))
            plt.grid(True)
            plt.show()