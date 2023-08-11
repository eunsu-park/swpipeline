from .base_dataset import BaseDataset
from astropy.io import fits
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

class EcallistoDataset(BaseDataset):
    def __init__(self, file_):
        super(EcallistoDataset, self).__init__(file_)
    #     self.parsing()

class EcallistoSpFitDataset(EcallistoDataset):
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        self.parsing_header()
        self.parsing_data()
        self.parsing_all()

    def parsing_header(self):
        hdu = fits.open(self.file_)
        header1 = hdu[0].header
        header2 = hdu[1].header
        self.header = [dict(header1.items()), dict(header2.items())]

    def parsing_data(self):
        hdu = fits.open(self.file_)
        data1 = hdu[0].data
        data2 = hdu[1].data
        self.data = [data1, data2]

    def parsing_all(self):
        all = [self.header, self.data]
        self.all = all

    def plot(self):
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
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = lines[0]
        data = lines[1:]
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        self.header = header

    def parsing_data(self, data):
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
    def __init__(self, file_):
        self.file_ = file_
        self.header = None
        self.data = None
        self.all = None

    def parsing(self):
        with open(self.file_, 'r') as file:
            lines = file.readlines()
        header = lines[:3]
        data = lines[3:]
        self.parsing_header(header)
        self.parsing_data(data)
        self.parsing_all()

    def parsing_header(self, header):
        self.header = header

    def parsing_data(self, data):
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