import numpy as np
import matplotlib.pyplot as plt
import datetime
import jdcal
import os
import time
import logging
import logging.handlers


import sys
sys.path.append("../lib")
from utilities import alert_message, check_directory


class Text_to_Image:
    def __init__(
        self,
        target_name,
        image_size,
        target_date,
        days=3,
        creadted_date=":Created",
        infor_end_string="--\n",
        data_name_check=False,
    ):
        self.original_data_list = []
        self.data_key_index = []
        self.creadted_data = []
        self.data_keys_list = []
        self.custom_data_list = {}
        self.target_file_path = []
        self.days = 0
        self.time_interval = 0

        self.target_name = target_name
        self.image_size = image_size

        self.make_path_url(target_name, target_date, days)
        self.read_text(self.target_file_path)
        self.find_index(self.original_data_list, infor_end_string)
        pass_check = self.find_creadted_data(
            self.original_data_list, creadted_date)
        if pass_check:
            # print("test")
            self.make_dict_keys(
                self.original_data_list, self.data_key_index, check=data_name_check
            )
            data_pass_check = self.data_extraction(
                self.original_data_list, self.data_key_index, self.data_keys_list
            )
            if data_pass_check:
                # print("test1")
                self.check_time_interval(self.original_data_list)
                image_path = (
                    self.creadted_data[0]
                    + "/"
                    + self.creadted_data[0]
                    + self.creadted_data[1]
                )
                ############## mkdir ################
                check_directory(image_path+"/")
                #####################################
                dir_path = self.check_and_make_dir(image_path)
                self.make_image(self.target_name, self.image_size, dir_path)
#            else:
#                os.chdir("/SpaceWeatherPy/")
#                with open("testlog/image_log.txt", "a+") as f:
#                    f.write(str(datetime.datetime.now()))
#                    f.write(" - today data not found\n")

    def make_path_url(self, target_name, target_date, days=3):
        standard_date = 0
        year = 0
        month = 0
        day = 0
        check_day = 0
        root_path = ""
        if type(target_date) == int:
            standard_date = str(target_date)
            year = standard_date[:4]
            month = standard_date[4:6]
            day = standard_date[6:8]
            days = days
            self.days = days
            check_day = int(day) - days
        else:
            standard_date = str(target_date[-1])
            year = standard_date[:4]
            month = standard_date[4:6]
            day = standard_date[6:8]
            days = target_date[-1] - target_date[0]
            self.days = days
            check_day = int(day) - days
        if target_name == "particle":
            #            root_path = "/NAS/ioGuard/vol7/swc/data/sec/goes/particle/"
            root_path = "/NAS/ioGuard/vol7/swc/data/noaa/swpc/goes/particle/"
            # root_path = "/Users/byeongchae/Desktop/project_6/2020/tt"
        elif target_name == "xray":
            #            root_path = "/NAS/ioGuard/vol7/swc/data/sec/goes/xray/"
            root_path = "/NAS/ioGuard/vol7/swc/data/noaa/swpc/goes/xray/"
            # root_path = "/Users/byeongchae/Desktop/project_6/2020/test"

        if int(month) == 1 and check_day < 0:
            root_path1 = root_path + "/" + year
            root_path2 = root_path + "/" + str(int(year) - 1)
            target_file_list1 = os.listdir(root_path1)
            target_file_list1.sort()
            for i, value in enumerate(target_file_list1):
                if standard_date in value:
                    break
            for j in range(int(day)):
                self.target_file_path.append(
                    root_path1 + "/" + target_file_list1[i - j]
                )

            target_file_list2 = os.listdir(root_path2)
            target_file_list2.sort()
            for i, value in enumerate(target_file_list2):
                if standard_date in value:
                    break
            for j in range(-check_day):
                self.target_file_path.append(
                    root_path2 + "/" + target_file_list2[-j - 1]
                )
        else:
            root_path = root_path + "/" + year
            target_file_list = os.listdir(root_path)
            target_file_list.sort()
            for i, value in enumerate(target_file_list):
                if standard_date in value:
                    break
            for j in range(self.days):
                self.target_file_path.append(
                    root_path + "/" + target_file_list[i - j])

    def read_text(self, file_path):
        """
        텍스트 파일을 한줄씩 읽어서 리스트로 저장

        input
        ----------------------------
        file_path : file_path [list]

        result
        --------------
        self.original_data_list [list]
        """
        for i in file_path:
            with open(i, "r") as f:
                self.original_data_list.append(f.readlines())

    def find_index(self, data_list, key_string):
        """
        리스트로 저장된 텍스트 데이터에서 원하는 위치의 인덱스 찾기

        input
        --------------------------------------------------------
        data_list : read_text() 의 결과 - 리스트 형식으로 바꾼 텍스트 파일
        key_string : 찾으려고 하는 단어 또는 문장

        result
        --------------------------
        self.data_key_index [list]
        """
        for i in data_list:
            for j, value in enumerate(i):
                if key_string in value:
                    self.data_key_index.append(j)
                    break

    def find_creadted_data(self, data_list, key_string=":Created:"):
        pass_check = True
        temp_data = []
        for i in data_list:
            for j, value in enumerate(i):
                if key_string in value:
                    break
            temp_data.append(i[j].split(" "))
        temp_data.sort()
        date = temp_data[-1][1].split("-")
        try:
            self.creadted_data = [
                date[0],
                date[1],
                self.change_month(date[1]),
                date[2],
                temp_data[-1][2],
            ]
        except Exception as identifier:
            pass_check = False
 #           os.chdir("/SpaceWeatherPy/")
 #           with open("testlog/image_log.txt", "a+") as f:
 #               f.write(str(datetime.datetime.now()))
 #               f.write("No data")
 #               f.write("\n")

        return pass_check

    def check_time_interval(self, data_list, key_string="-minute"):
        pass_check = True
        data = self.original_data_list[-1]
        temp_data = ""
        for i, value in enumerate(data):
            if key_string in value:
                break
        temp_data = value.split(" ")
        try:
            while "" in temp_data:
                temp_data.remove("")
        except Exception as e:
            stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
            alert_message("while(1) json realtime is stopped: "+str(e), stopped_log_path)
        time = temp_data[1].split("-")
        self.time_interval = time[0]

    def change_month(self, number):
        number = int(number)
        if number == 1:
            month = "Jan"
        elif number == 2:
            month = "Feb"
        elif number == 3:
            month = "Mar"
        elif number == 4:
            month = "Apr"
        elif number == 5:
            month = "May"
        elif number == 6:
            month = "Jun"
        elif number == 7:
            month = "Jul"
        elif number == 8:
            month = "Aug"
        elif number == 9:
            month = "Sep"
        elif number == 10:
            month = "Oct"
        elif number == 11:
            month = "Nov"
        elif number == 12:
            month = "Dec"
        return month

    def make_dict_keys(
        self, data_list, data_key_index, start_index=6, end_index=None, check=False
    ):
        for i, value in enumerate(data_list):
            keys = ["date", "satellite"]
            temp_keys = value[data_key_index[i] - 1][:-1]
            temp_keys = temp_keys.split(" ")
            try:
                while "" in temp_keys:
                    temp_keys.remove("")
            except Exception as e:
                stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
                alert_message("while(2) json realtime is stopped: "+str(e), stopped_log_path)
            
            try:
                while "\n" in temp_keys:
                    temp_keys.remove("\n")
            except Exception as e:
                stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
                alert_message("while(3) json realtime is stopped: "+str(e), stopped_log_path)


            if check == True:
                print(temp_keys)
                exit(0)
            else:
                if end_index == None:
                    for j in range(start_index, len(temp_keys)):
                        keys.append(temp_keys[j])
                    self.data_keys_list.append(keys)
                else:
                    for j in range(start_index, end_index + 1):
                        keys.append(temp_keys[j])
                    self.data_keys_list.append(keys)

    def data_extraction(self, data_list, data_key_index, data_keys_list):
        pass_check = True
        for i, value in enumerate(data_list):
            temp_dict = {}
            for index1, value1 in enumerate(data_keys_list[i]):
                temp_dict[value1] = []

            j = data_key_index[i] + 1
            if j < len(value):
                for k in range(j, len(value)):
                    data = value[k][:-1]
                    data = data.split("\t")
                    try:
                        while "" in data:
                            data.remove("")
                    except Exception as e:
                        stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
                        alert_message("while(4) json realtime is stopped: "+str(e), stopped_log_path)

                    for index2, value2 in enumerate(data_keys_list[i]):
                        temp_dict[value2].append(data[index2])

                self.custom_data_list[i] = temp_dict
            elif j == len(value):
                pass_check *= False

        return pass_check

    def conversion_custom_JD(self, date):
        JD = []
        for i in date:
            temp_data = i.split(" ")
            try:
                while "" in temp_data:
                    temp_data.remove("")
            except Exception as e:
                stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
                alert_message("while(5) json realtime is stopped: "+str(e), stopped_log_path)

            jd = jdcal.gcal2jd(int(temp_data[0]), int(
                temp_data[1]), int(temp_data[2]))
            m = int(temp_data[-1][:2]) * 60
            m = m + int(temp_data[-1][2:])
            m = m / 1440
            JD.append((jd[1] + m))

        return JD

    # def check_time_interval(self, date):
    #     time_interval = int(date[1][-4:]) - int(date[0][-4:])

    #     return time_interval

    def check_and_make_dir(self, save_path):
        tg_path = "/NAS/ioGuard/vol7/swc/data/kasi/swms/" 
        ############## mkdir ################
        print(tg_path)
        check_directory(tg_path)
        #####################################
        os.chdir(tg_path)
        temp_list = save_path.split("/")
        try:
            while "" in temp_list:
                temp_list.remove("")
        except Exception as e:
            stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
            alert_message("while(6) json realtime is stopped: "+str(e), stopped_log_path)


        temp_path = ""
        if os.path.isdir(save_path) == True:
            temp_path = save_path
        else:
            for i in temp_list:
                temp_path += i
                if os.path.isdir(temp_path):
                    temp_path += "/"
                else:
                    os.mkdir(temp_path)
                    temp_path += "/"

        return temp_path

    def make_image(self, name, size, dir_path):

        if name == "particle":
            satellite_number = self.custom_data_list[0]["satellite"][0]
            time_interval = self.time_interval
            x_list = []
            y_list = []
            for i in range(self.days):
                x_list.append(
                    self.conversion_custom_JD(self.custom_data_list[i]["date"])
                )
                y_list.append(
                    list(map(float, self.custom_data_list[i]["P>10"])))
                y_list.append(
                    list(map(float, self.custom_data_list[i]["P>50"])))
                y_list.append(
                    list(map(float, self.custom_data_list[i]["P>100"])))

            temp_x_sum = np.array([])
            for i in range(self.days):
                temp_x_sum = np.append(temp_x_sum, np.array(x_list[i]))
            temp_x_sum = np.sort(temp_x_sum)

            min_date = np.min(temp_x_sum)
            max_date = min_date + self.days
            x_range = [min_date, max_date]

            temp_date = np.linspace(min_date, max_date, self.days + 1)
            date_list = []
            for i in temp_date:
                ttt = jdcal.jd2gcal(2400000.5, int(i))
                if ttt[1] == 1:
                    mon = "Jan"
                elif ttt[1] == 2:
                    mon = "Feb"
                elif ttt[1] == 3:
                    mon = "Mar"
                elif ttt[1] == 4:
                    mon = "Apr"
                elif ttt[1] == 5:
                    mon = "May"
                elif ttt[1] == 6:
                    mon = "Jun"
                elif ttt[1] == 7:
                    mon = "Jul"
                elif ttt[1] == 8:
                    mon = "Aug"
                elif ttt[1] == 9:
                    mon = "Sep"
                elif ttt[1] == 10:
                    mon = "Oct"
                elif ttt[1] == 11:
                    mon = "Nov"
                elif ttt[1] == 12:
                    mon = "Dec"
                date_value = mon + " " + str(ttt[2])
                date_list.append(date_value)

            if size == 600:
                fig = plt.figure(figsize=(6, 5), dpi=100)
                fig.subplots_adjust(bottom=0.14, top=0.9)
                ax = plt.axes()
                plt.rcParams["font.size"] = 8
                plt.rcParams["font.stretch"] = 0
                color_list = [(1, 0, 0), (0, 0, 1), (0, 1, 0)]
                for i in range(3):
                    for j in range(self.days):
                        plt.semilogy(
                            x_list[j],
                            y_list[i + 3 * j],
                            color=color_list[i],
                            linewidth=1,
                        )
                    # plt.semilogy(x1, y11, color=(1, 0, 0), linewidth=1)
                    # plt.semilogy(x2, y21, color=(1, 0, 0), linewidth=1)
                    # plt.semilogy(x3, y31, color=(1, 0, 0), linewidth=1)
                    # plt.semilogy(x1, y12, color=(0, 0, 1), linewidth=1)
                    # plt.semilogy(x2, y22, color=(0, 0, 1), linewidth=1)
                    # plt.semilogy(x3, y32, color=(0, 0, 1), linewidth=1)
                    # plt.semilogy(x1, y13, color=(0, 1, 0), linewidth=1)
                    # plt.semilogy(x2, y23, color=(0, 1, 0), linewidth=1)
                    # plt.semilogy(x3, y33, color=(0, 1, 0), linewidth=1)

                plt.ylim(1e-2, 1e4)
                plt.xlim(x_range[0], x_range[-1])
                ax.set_xticks(
                    np.linspace(np.min(x_range), np.max(
                        x_range), self.days + 1)
                )
                ax.set_xticklabels(date_list, position=(0, -0.02), size=8)
                ax.tick_params(
                    axis="both",
                    direction="in",
                    which="both",
                    top=True,
                    right=True,
                    labelsize=8,
                )
                ax.tick_params(axis="both", which="minor", length=3)
                ax.tick_params(axis="both", which="major", length=4)
                ax.set_xticks(
                    np.linspace(np.min(x_range), np.max(
                        x_range), self.days * 12 + 1),
                    minor=True,
                )

                plt.title(
                    "GOES{} Proton Flux({} min)".format(
                        satellite_number, time_interval
                    ),
                    position=(0.5, 1.03),
                )
                plt.ylabel(
                    "[particles cm$^{-2}$ s$^{-1}$ sr$^{-1}$]",
                    fontdict={"fontsize": 10},
                )
                infor_text = "Updated {} {} {} {} [UTC]\nKorea Astronomy and Space Science Institute / Space Weather Research Center".format(
                    self.creadted_data[0],
                    self.creadted_data[2],
                    self.creadted_data[3],
                    self.creadted_data[4],
                )
                ax.text(
                    0.125, 0.015, infor_text, transform=plt.gcf().transFigure,
                )

                plt.grid(axis="y", linestyle="-", color="black")
                plt.grid(axis="x", linestyle="--",
                         which="major", color="black")

                tt = np.array([1e3, 1e2, 1e1])
                te = 1 + (np.log10(tt) - 4) / 6
                tc = np.array([1 + te[0], te[0] + te[1], te[1] + te[2]]) / 2
                tx = np.ones(5) * 1.02
                r_text = np.array(["S3", "S2", "S1"])
                plt.fill_between(x_range, 1e4, 1e3, color=(1, 1, 204 / 255))
                plt.fill_between(x_range, 1e3, 1e2,
                                 color=(204 / 255, 1, 204 / 255))
                plt.fill_between(x_range, 1e2, 1e1,
                                 color=(204 / 255, 213 / 255, 1))
                for i in range(3):
                    ax.text(
                        tx[i],
                        tc[i],
                        r_text[i],
                        {"color": "black", "fontsize": 10},
                        horizontalalignment="left",
                        verticalalignment="center",
                        transform=plt.gca().transAxes,
                    )

                ax.text(
                    1.085,
                    4 / 12,
                    r"$\geq 100$",
                    {"color": (0, 1, 0), "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                ax.text(
                    1.085,
                    5.5 / 12,
                    r"$\geq 50$",
                    {"color": (0, 0, 1), "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                ax.text(
                    1.085,
                    7 / 12,
                    r"$\geq 10$",
                    {"color": (1, 0, 0), "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                ax.text(
                    1.085,
                    8.5 / 12,
                    r"[MeV]",
                    {"color": "black", "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                plt.savefig(
                    "{}/sec_goes{}_proton_600_{}{}{}.png".format(
                        dir_path,
                        satellite_number,
                        self.creadted_data[0],
                        self.creadted_data[1],
                        self.creadted_data[3],
                    )
                )
                plt.close()

            elif size == 400:
                fig = plt.figure(figsize=(4, 1.5), dpi=100)
                fig.subplots_adjust(bottom=0.14, top=0.86)
                ax = plt.axes()

                plt.rcParams["font.size"] = 8
                plt.rcParams["font.stretch"] = 0

                #
                color_list = [(1, 0, 0), (0, 0, 1), (0, 1, 0)]
                for i in range(3):
                    for j in range(self.days):
                        plt.semilogy(
                            x_list[j],
                            y_list[i + 3 * j],
                            color=color_list[i],
                            linewidth=1,
                        )
                # plt.semilogy(x1, y11, color=(1, 0, 0), linewidth=1)
                # plt.semilogy(x2, y21, color=(1, 0, 0), linewidth=1)
                # plt.semilogy(x3, y31, color=(1, 0, 0), linewidth=1)
                # plt.semilogy(x1, y12, color=(0, 0, 1), linewidth=1)
                # plt.semilogy(x2, y22, color=(0, 0, 1), linewidth=1)
                # plt.semilogy(x3, y32, color=(0, 0, 1), linewidth=1)
                # plt.semilogy(x1, y13, color=(0, 1, 0), linewidth=1)
                # plt.semilogy(x2, y23, color=(0, 1, 0), linewidth=1)
                # plt.semilogy(x3, y33, color=(0, 1, 0), linewidth=1)

                plt.ylim(1e-2, 1e4)
                plt.xlim(x_range[0], x_range[-1])
                ax.set_xticks(
                    np.linspace(np.min(x_range), np.max(
                        x_range), self.days + 1)
                )
                ax.set_xticklabels(date_list, position=(0, -0.02), size=6)
                ax.tick_params(axis="y", labelsize=8, pad=0.2, size=6)
                ax.tick_params(
                    axis="both",
                    direction="in",
                    which="both",
                    top=True,
                    right=True,
                    labelsize=8,
                )
                ax.tick_params(axis="both", which="minor", length=2)
                ax.tick_params(axis="both", which="major", length=2)
                ax.set_xticks(
                    np.linspace(np.min(x_range), np.max(
                        x_range), self.days * 4 + 1),
                    minor=True,
                )
                ax.set_yticks([0.01, 0.1, 1, 10, 100, 1000, 10000])
                ax.minorticks_on()

                log_find_flag = ax.get_ylim()[0]
                log_array = np.array([])
                try:
                    while log_find_flag < ax.get_ylim()[1]:
                        log_array = np.append(
                            log_array, np.linspace(
                                log_find_flag, log_find_flag * 9, 5)
                        )
                        log_find_flag = log_find_flag * 10
                except Exception as e:
                    stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
                    alert_message("while(7) json realtime is stopped: "+str(e), stopped_log_path)


                ax.set_yticks(log_array, minor=True)
                plt.title(
                    "GOES{} Proton Flux({} min)".format(
                        satellite_number, time_interval
                    ),
                    position=(0.5, 0.97),
                )
                plt.ylabel(
                    "Particles cm$^{-2}$ s$^{-1}$ sr$^{-1}$",
                    fontdict={"fontsize": 8},
                    labelpad=-1,
                )

                plt.grid(axis="y", linestyle="-", color="black")
                plt.grid(axis="x", linestyle="--",
                         which="major", color="black")

                tt = np.array([1e3, 1e2, 1e1])
                te = 1 + (np.log10(tt) - 4) / 6
                tc = np.array([1 + te[0], te[0] + te[1], te[1] + te[2]]) / 2
                tx = np.ones(5) * 1.02
                r_text = np.array(["S3", "S2", "S1"])

                plt.fill_between(x_range, 1e4, 1e3, color=(1, 1, 204 / 255))
                plt.fill_between(x_range, 1e3, 1e2,
                                 color=(204 / 255, 1, 204 / 255))
                plt.fill_between(x_range, 1e2, 1e1,
                                 color=(204 / 255, 213 / 255, 1))
                for i in range(3):
                    ax.text(
                        tx[i],
                        tc[i],
                        r_text[i],
                        {"color": "black", "fontsize": 10},
                        horizontalalignment="left",
                        verticalalignment="center",
                        transform=plt.gca().transAxes,
                    )

                ax.text(
                    1.085,
                    0,
                    r"$\geq 100$",
                    {"color": (0, 1, 0), "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                ax.text(
                    1.085,
                    4 / 12,
                    r"$\geq 50$",
                    {"color": (0, 0, 1), "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                ax.text(
                    1.085,
                    8 / 12,
                    r"$\geq 10$",
                    {"color": (1, 0, 0), "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                ax.text(
                    1.085,
                    1,
                    r"[MeV]",
                    {"color": "black", "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                plt.savefig(
                    "{}/sec_goes{}_proton_400_{}{}{}.png".format(
                        dir_path,
                        satellite_number,
                        self.creadted_data[0],
                        self.creadted_data[1],
                        self.creadted_data[3],
                    )
                )
                plt.close()

        elif name == "xray":
            satellite_number = self.custom_data_list[0]["satellite"][0]
            time_interval = self.time_interval

            x_list = []
            y_list = []
            for i in range(self.days):
                x_list.append(
                    self.conversion_custom_JD(self.custom_data_list[i]["date"])
                )
                y_list.append(
                    list(map(float, self.custom_data_list[i]["Short"])))
                y_list.append(
                    list(map(float, self.custom_data_list[i]["Long"])))

            x_range = np.array([])
            for i in range(self.days):
                x_range = np.append(x_range, np.array(x_list[i]))
            x_range = np.sort(x_range)

            temp_x_sum = np.array([])
            for i in range(self.days):
                temp_x_sum = np.append(temp_x_sum, np.array(x_list[i]))
            temp_x_sum = np.sort(temp_x_sum)

            min_date = np.min(temp_x_sum)
            max_date = min_date + self.days
            x_range = [min_date, max_date]

            temp_date = np.linspace(min_date, max_date, self.days + 1)
            date_list = []
            for i in temp_date:
                ttt = jdcal.jd2gcal(2400000.5, int(i))
                if ttt[1] == 1:
                    mon = "Jan"
                elif ttt[1] == 2:
                    mon = "Feb"
                elif ttt[1] == 3:
                    mon = "Mar"
                elif ttt[1] == 4:
                    mon = "Apr"
                elif ttt[1] == 5:
                    mon = "May"
                elif ttt[1] == 6:
                    mon = "Jun"
                elif ttt[1] == 7:
                    mon = "Jul"
                elif ttt[1] == 8:
                    mon = "Aug"
                elif ttt[1] == 9:
                    mon = "Sep"
                elif ttt[1] == 10:
                    mon = "Oct"
                elif ttt[1] == 11:
                    mon = "Nov"
                elif ttt[1] == 12:
                    mon = "Dec"
                date_value = mon + " " + str(ttt[2])
                date_list.append(date_value)

            if size == 600:
                fig = plt.figure(figsize=(6, 5), dpi=100)
                fig.subplots_adjust(bottom=0.14, top=0.9)
                # ax = fig.add_subplot(1,1,1)
                ax = plt.axes()
                plt.rcParams["font.size"] = 8
                plt.rcParams["font.stretch"] = 0

                #
                color_list = [(1, 0, 0), (0, 0, 1)]
                for i in range(2):
                    for j in range(self.days):
                        plt.semilogy(
                            x_list[j],
                            y_list[i + 2 * j],
                            color=color_list[i],
                            linewidth=1,
                        )

                plt.ylim(1e-10, 1e-2)
                plt.xlim(x_range[0], x_range[-1])
                ax.set_xticks(
                    np.linspace(np.min(x_range), np.max(
                        x_range), self.days + 1)
                )
                ax.set_xticklabels(date_list, position=(0, -0.02), size=8)
                ax.tick_params(
                    axis="both",
                    direction="in",
                    which="both",
                    top=True,
                    right=True,
                    labelsize=8,
                )
                ax.tick_params(axis="both", which="minor", length=3)
                ax.tick_params(axis="both", which="major", length=4)
                ax.set_xticks(
                    np.linspace(np.min(x_range), np.max(
                        x_range), self.days * 12 + 1),
                    minor=True,
                )
                ax.set_yticks([1e-10, 1e-9, 1e-8, 1e-7,
                               1e-6, 1e-5, 1e-4, 1e-3, 1e-2])
                ax.tick_params(axis='y', labelsize=8)
                log_find_flag = ax.get_ylim()[0]
                log_array = np.array([])
                try:
                    while log_find_flag < ax.get_ylim()[1]:
                        log_array = np.append(
                            log_array, np.linspace(
                                log_find_flag, log_find_flag * 9, 9)
                        )
                        log_find_flag = log_find_flag * 10
                except Exception as e:
                    stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
                    alert_message("while(8) json realtime is stopped: "+str(e), stopped_log_path)


                ax.set_yticks(log_array, minor=True)

                plt.title(
                    "GOES{} X-ray Flux({} min)".format(satellite_number,
                                                       time_interval),
                    position=(0.5, 1.03),
                )
                plt.ylabel(
                    "[Watt m$^{-2}$]", fontdict={"fontsize": 10}, labelpad=-5,
                )
                infor_text = "Updated {} {} {} {} [UTC]\nKorea Astronomy and Space Science Institute / Space Weather Research Center".format(
                    self.creadted_data[0],
                    self.creadted_data[2],
                    self.creadted_data[3],
                    self.creadted_data[4],
                )
                ax.text(
                    0.125, 0.015, infor_text, transform=plt.gcf().transFigure,
                )

                plt.grid(axis="y", linestyle="-", color="black")
                plt.grid(axis="x", linestyle="--",
                         which="major", color="black")

                tt = np.array([2e-3, 1e-3, 1e-4, 5e-5, 1e-5])
                te = 1 + (np.log10(tt) + 2) / 8
                tc = (
                    np.array(
                        [
                            1 + te[0],
                            te[0] + te[1],
                            te[1] + te[2],
                            te[2] + te[3],
                            te[3] + te[4],
                        ]
                    )
                    / 2
                )
                tx = np.ones(5) * 1.01
                r_text = np.array(["R5", "R4", "R3", "R2", "R1"])
                plt.fill_between(x_range, 1, 2e-3,
                                 color=(1, 158 / 255, 140 / 255))
                plt.fill_between(x_range, 2e-3, 1e-3,
                                 color=(1, 213 / 255, 204 / 255))
                plt.fill_between(x_range, 1e-3, 1e-4, color=(1, 1, 204 / 255))
                plt.fill_between(x_range, 1e-4, 5e-5,
                                 color=(203 / 255, 1, 203 / 255))
                plt.fill_between(x_range, 5e-5, 1e-5,
                                 color=(204 / 255, 213 / 255, 1))
                for i in range(5):
                    ax.text(
                        tx[i],
                        tc[i],
                        r_text[i],
                        {"color": "black", "fontsize": 10},
                        horizontalalignment="left",
                        verticalalignment="center",
                        transform=plt.gca().transAxes,
                    )

                plt.text(
                    1.07,
                    0.65,
                    r"1.0-8.0A",
                    {"color": "red", "fontsize": 10},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                plt.text(
                    1.07,
                    0.35,
                    r"0.5-4.0A",
                    {"color": "blue", "fontsize": 10},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                plt.savefig(
                    "{}/sec_goes{}_xray_600_{}{}{}.png".format(
                        dir_path,
                        satellite_number,
                        self.creadted_data[0],
                        self.creadted_data[1],
                        self.creadted_data[3],
                    )
                )
                plt.close()

            elif size == 400:
                satellite_number = self.custom_data_list[0]["satellite"][0]
                time_interval = self.time_interval
                fig = plt.figure(figsize=(4, 1.5), dpi=100)
                fig.subplots_adjust(bottom=0.14, top=0.86)
                # ax = fig.add_subplot(1,1,1)
                ax = plt.axes()

                plt.rcParams["font.size"] = 8
                plt.rcParams["font.stretch"] = 0
                # plt.tight_layout()
                color_list = [(1, 0, 0), (0, 0, 1)]
                for i in range(2):
                    for j in range(self.days):
                        plt.semilogy(
                            x_list[j],
                            y_list[i + 2 * j],
                            color=color_list[i],
                            linewidth=1,
                        )

                plt.ylim(1e-10, 1e-2)
                plt.xlim(x_range[0], x_range[-1])
                ax.set_xticks(
                    np.linspace(np.min(x_range), np.max(
                        x_range), self.days + 1)
                )
                ax.set_xticklabels(date_list, position=(0, -0.02), size=6)
                ax.tick_params(axis="y", labelsize=8, pad=0.2, size=6)
                ax.tick_params(
                    axis="both",
                    direction="in",
                    which="both",
                    top=True,
                    right=True,
                    labelsize=8,
                )
                ax.tick_params(axis="both", which="minor", length=2)
                ax.tick_params(axis="both", which="major", length=2)
                ax.set_xticks(
                    np.linspace(np.min(x_range), np.max(
                        x_range), self.days * 4 + 1),
                    minor=True,
                )
                ax.set_yticks([1e-10, 1e-9, 1e-8, 1e-7,
                               1e-6, 1e-5, 1e-4, 1e-3, 1e-2])
                ax.minorticks_on()

                log_find_flag = ax.get_ylim()[0]
                log_array = np.array([])
                try:
                    while log_find_flag < ax.get_ylim()[1]:
                        log_array = np.append(
                            log_array, np.linspace(
                                log_find_flag, log_find_flag * 9, 5)
                        )
                        log_find_flag = log_find_flag * 10
                except Exception as e:
                    stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
                    alert_message("while(9) json realtime is stopped: "+str(e), stopped_log_path)
                ax.set_yticks(log_array, minor=True)
                plt.title(
                    "GOES{} X-ray Flux({} min)".format(satellite_number,
                                                       time_interval),
                    position=(0.5, 0.97),
                )
                plt.ylabel(
                    "[Watt m$^{-2}$]", fontdict={"fontsize": 8}, labelpad=-5,
                )
                # infor_text = "Updated {} [UTC]\nKorea Astronomy and Space Science Institute / Space Weather Research Center".format(
                #     self.custom_data_list[0]["date"][0]
                # )
                # ax.text(
                #     0.125, 0.015, infor_text, transform=plt.gcf().transFigure,
                # )

                plt.grid(axis="y", linestyle="-", color="black")
                plt.grid(axis="x", linestyle="--",
                         which="major", color="black")

                tt = np.array([2e-3, 1e-3, 1e-4, 5e-5, 1e-5])
                te = 1 + (np.log10(tt) + 2) / 8
                tc = (
                    np.array(
                        [
                            1 + te[0],
                            te[0] + te[1] - 0.02,
                            te[1] + te[2] - 0.015,
                            te[2] + te[3] - 0.02,
                            te[3] + te[4] - 0.05,
                        ]
                    )
                    / 2
                )
                tx = np.ones(5) * 1.02
                r_text = np.array(["R5", "R4", "R3", "R2", "R1"])
                plt.fill_between(x_range, 1, 2e-3,
                                 color=(1, 158 / 255, 140 / 255))
                plt.fill_between(x_range, 2e-3, 1e-3,
                                 color=(1, 213 / 255, 204 / 255))
                plt.fill_between(x_range, 1e-3, 1e-4, color=(1, 1, 204 / 255))
                plt.fill_between(x_range, 1e-4, 5e-5,
                                 color=(203 / 255, 1, 203 / 255))
                plt.fill_between(x_range, 5e-5, 1e-5,
                                 color=(204 / 255, 213 / 255, 1))

                for i in range(5):
                    ax.text(
                        tx[i],
                        tc[i],
                        r_text[i],
                        {"color": "black", "fontsize": 6, "weight": "light"},
                        horizontalalignment="left",
                        verticalalignment="center",
                        transform=plt.gca().transAxes,
                    )

                plt.text(
                    1.085,
                    0.8,
                    r"1.0-8.0A",
                    {"color": (1, 0, 0), "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                plt.text(
                    1.085,
                    0.3,
                    r"0.5-4.0A",
                    {"color": (0, 0, 1), "fontsize": 8},
                    horizontalalignment="left",
                    verticalalignment="center",
                    rotation=90,
                    transform=plt.gca().transAxes,
                )

                plt.savefig(
                    "{}/sec_goes{}_xray_400_{}{}{}.png".format(
                        dir_path,
                        satellite_number,
                        self.creadted_data[0],
                        self.creadted_data[1],
                        self.creadted_data[3],
                    )
                )
                plt.close()


########## download old data ##########
"""
fr = 20201109
to = 20201116

fr_str = str(fr)
to_str = str(to)

fr_date = datetime.datetime.strptime(fr_str, "%Y%m%d")
to_date = datetime.datetime.strptime(to_str, "%Y%m%d")

day_count = (to_date-fr_date).days + 1

date = fr_date

for i in range(day_count):
    target_date = int(date.strftime("%Y%m%d"))
    print(target_date)
    
    Text_to_Image("xray", 600, target_date)
    Text_to_Image("xray", 400, target_date)
    Text_to_Image("particle", 600, target_date)
    Text_to_Image("particle", 400, target_date)
    
    date += datetime.timedelta(days=1)

print("Recovery complete.")
exit(0)
"""
#######################################


# for i in range(13):
#     target_date = 20200401 + int(i)
#     Text_to_Image("xray", 600, target_date)
#     Text_to_Image("xray", 400, target_date)
#     Text_to_Image("particle", 600, target_date)
#     Text_to_Image("particle", 400, target_date)
#     print('check')
# #
# print('end')
# exit(0)
# target_date = 20200428
# Text_to_Image("xray", 600, target_date)
# Text_to_Image("xray", 400, target_date)
# Text_to_Image("particle", 600, target_date)
# Text_to_Image("particle", 400, target_date)
# print(target_date)
# print('check')
# target_date = 20200429
# Text_to_Image("xray", 600, target_date)
# Text_to_Image("xray", 400, target_date)
# Text_to_Image("particle", 600, target_date)
# Text_to_Image("particle", 400, target_date)
# print(target_date)
# print('check')
# target_date = 20200430
# Text_to_Image("xray", 600, target_date)
# Text_to_Image("xray", 400, target_date)
# Text_to_Image("particle", 600, target_date)
# Text_to_Image("particle", 400, target_date)
# print(target_date)
# print('check')
# target_date = 20200501
# Text_to_Image("xray", 600, target_date)
# Text_to_Image("xray", 400, target_date)
# Text_to_Image("particle", 600, target_date)
# Text_to_Image("particle", 400, target_date)
# print(target_date)
# print('check')
# target_date = 20200502
# Text_to_Image("xray", 600, target_date)
# Text_to_Image("xray", 400, target_date)
# Text_to_Image("particle", 600, target_date)
# Text_to_Image("particle", 400, target_date)
# print(target_date)
# print('check')


#target_date = 20200814
#Text_to_Image("xray", 600, target_date)
#Text_to_Image("xray", 400, target_date)
#Text_to_Image("particle", 600, target_date)
#Text_to_Image("particle", 400, target_date)
#target_date = 20200815
#Text_to_Image("xray", 600, target_date)
#Text_to_Image("xray", 400, target_date)
#Text_to_Image("particle", 600, target_date)
#Text_to_Image("particle", 400, target_date)
#target_date = 20200816
#Text_to_Image("xray", 600, target_date)
#Text_to_Image("xray", 400, target_date)
#Text_to_Image("particle", 600, target_date)
#Text_to_Image("particle", 400, target_date)
#target_date = 20200817
#Text_to_Image("xray", 600, target_date)
#Text_to_Image("xray", 400, target_date)
#Text_to_Image("particle", 600, target_date)
#Text_to_Image("particle", 400, target_date)
#target_date = 20200818
#Text_to_Image("xray", 600, target_date)
#Text_to_Image("xray", 400, target_date)
#Text_to_Image("particle", 600, target_date)
#Text_to_Image("particle", 400, target_date)
#target_date = 20200819
#Text_to_Image("xray", 600, target_date)
#Text_to_Image("xray", 400, target_date)
#Text_to_Image("particle", 600, target_date)
#Text_to_Image("particle", 400, target_date)
'''
print("test\n")
target_date = 20201103
Text_to_Image("xray", 600, target_date)
Text_to_Image("xray", 400, target_date)
Text_to_Image("particle", 600, target_date)
Text_to_Image("particle", 400, target_date)
print("test\n")

print("test\n")
target_date = 20201104
Text_to_Image("xray", 600, target_date)
Text_to_Image("xray", 400, target_date)
Text_to_Image("particle", 600, target_date)
Text_to_Image("particle", 400, target_date)
print("test\n")

exit(0)
'''

# fr = 20210101
# to = 20210104

# fr_str = str(fr)
# to_str = str(to)

# fr_date = datetime.datetime.strptime(fr_str, "%Y%m%d")
# to_date = datetime.datetime.strptime(to_str, "%Y%m%d")

# day_count = (to_date-fr_date).days + 1

# date = fr_date

# for i in range(day_count):
#     target_date = int(date.strftime("%Y%m%d"))
#     print(target_date)
    
#     Text_to_Image("xray", 600, target_date)
#     Text_to_Image("xray", 400, target_date)
#     Text_to_Image("particle", 600, target_date)
#     Text_to_Image("particle", 400, target_date)
    
#     date += datetime.timedelta(days=1)

# print("Recovery complete.")
# exit(0)





make_image = True
log_path = "/SpaceWeatherPy/log/image_log/"

image_Logger = logging.getLogger()
image_Logger.setLevel(logging.INFO)
if(not os.path.exists(log_path)):
    ############## mkdir ################
    os.makedirs(log_path, exist_ok=True)
    #####################################
    # os.mkdir(log_path, True)
# os.chdir("/SpaceWeatherPy/log/")
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename= os.path.join(log_path, "image_log.log"), when='midnight', interval=1, utc=True, encoding='utf-8')
# file_handler = logging.FileHandler(
#     'json_log/{:%Y%m%d}.log'.format(datetime.datetime.utcnow()))
formatter = logging.Formatter(
    '[%(asctime)s]\t[%(levelname)s | %(filename)s : %(lineno)d]  >>  %(message)s')
logging.Formatter.converter = time.gmtime
file_handler.setFormatter(formatter)
image_Logger.addHandler(file_handler)


def make_images(time_inter):
    ###################### realtime stopped log #########################
    stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
    alert_message("image realtime is started", stopped_log_path)
    #############################################################
    try:
        while make_image:
            raw_date = datetime.datetime.utcnow()
            target_date = raw_date.strftime("%H%M")
            if target_date == "0017":
                date_time = datetime.datetime.utcnow() - datetime.timedelta(days=1)
                target_date = int(date_time.strftime("%Y%m%d"))
                Text_to_Image("xray", 600, target_date)
                Text_to_Image("xray", 400, target_date)
                Text_to_Image("particle", 600, target_date)
                Text_to_Image("particle", 400, target_date)
                os.chdir("/SpaceWeatherPy/")
                image_Logger.info("yesterday image make")
                # os.chdir("/SpaceWeatherPy/")
                # with open("testlog/image_log.txt", "a+") as f:
                #     f.write(str(datetime.datetime.now()))
                #     f.write("yesterday image make")
                #     f.write("\n")
                time.sleep(50)
            elif time.time() % time_inter < 0.5:
                time.sleep(25)
                date_time = datetime.datetime.utcnow()
                target_date = int(date_time.strftime("%Y%m%d"))
                Text_to_Image("xray", 600, target_date)
                Text_to_Image("xray", 400, target_date)
                Text_to_Image("particle", 600, target_date)
                Text_to_Image("particle", 400, target_date)
                os.chdir("/SpaceWeatherPy/")
                image_Logger.info("Image creation success")
                # os.chdir("/SpaceWeatherPy/")
                # with open("testlog/image_log.txt", "a+") as f:
                #     f.write(str(datetime.datetime.now()))
                #     f.write("\n")
    # except Exception as e:
    #     image_Logger.info(e)
    #     make_images(time_inter)
    ###################### realtime stopped log #########################
    except Exception as e:
        alert_message("image realtime is stopped: "+str(e), stopped_log_path)
        #############################################################
        time.sleep(1)
        make_images(300)

def stop_make_images():
    make_image = False

###################### realtime stopped log #########################
stopped_log_path = "/SpaceWeatherPy/log/realtime_program_stopped/make_new_image.log"
alert_message("################ RUN PROGRAM ###############", stopped_log_path)
#############################################################
make_images(300)



