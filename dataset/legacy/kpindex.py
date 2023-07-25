import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import datetime
import time
import sys

from numpy.lib.shape_base import split

data_root_path = "/NAS/ioGuard/vol7/swc/data/noaa/swpc/dayindices"
image_root_path = "/NAS/ioGuard/vol7/swc/data/kasi/swms"

# data_root_path = "GOES_bar_graph"
# image_root_path = "GOES_bar_graph"

def read_file(file_path):

    try:
        with open(file_path, "r") as f:
            data_list = f.readlines()

        return data_list
    except FileNotFoundError:
        print("FileNotFoundError : %s"%(file_path))
        return []

def parse_data(data_list, target_date_check = False):
    target_data_line = data_list[-1]

    split_target_data = target_data_line.split('\n')[0].split(' ')
    target_data_string = list(filter(("").__ne__, split_target_data))[-8:]

    for iter, data in enumerate(target_data_string):
        if data == '-1' or float(data) <= -1:
            if target_date_check == False:
                target_data_string[iter] = 0
            else:
                return []

    # print(target_data_string)
    target_data_int = list(map(float, target_data_string))
    return target_data_int

def make_data_color(data):
    color_list = []

    for value in data:

        if value < 4:
            color_list.append('green')
        elif value == 4:
            color_list.append('#f7e920')
        else:
            color_list.append('red')
    
    return color_list

def make_date_tick(target_date):
    """
    target_date : 'YYYY-MM-DD'
    """
    # upto python 3.7
    if sys.version_info >= (3, 7):
        today = datetime.date.fromisoformat(target_date)
    else:
        split_date = target_date.split("-")
        year = int(split_date[0])
        month = int(split_date[1])
        day = int(split_date[2])
        today = datetime.date(year, month, day)


    yesterday = today - datetime.timedelta(days=1)
    before_yesterday = today - datetime.timedelta(days=2)
    tomorrow = today + datetime.timedelta(days=1)

    date_list = [before_yesterday.strftime("%b %d"), yesterday.strftime("%b %d"), today.strftime("%b %d"), tomorrow.strftime("%b %d")]

    return date_list

def make_image(target_date = None):

    target_date_check = False
    if target_date == None:
        today = datetime.datetime.utcnow()
        today_path = data_root_path + today.strftime("/curind.txt")
    else:
        if sys.version_info >= (3, 7):
            today = datetime.date.fromisoformat(target_date)
        else:
            split_date = target_date.split("-")
            year = int(split_date[0])
            month = int(split_date[1])
            day = int(split_date[2])
            today = datetime.date(year, month, day)

        target_date_check = True
        today_path = data_root_path + today.strftime("/%Y/%Y%m%ddayind.txt")

    yesterday = today - datetime.timedelta(days=1)
    before_yesterday = today - datetime.timedelta(days=2)

    yesterday_path = data_root_path + yesterday.strftime("/%Y/%Y%m%ddayind.txt")
    before_yesterday_path = data_root_path + before_yesterday.strftime("/%Y/%Y%m%ddayind.txt")
    
    data_list = []

    read_buffer = None
    read_buffer = read_file(before_yesterday_path)
    if len(read_buffer) == 0:
        data_list += [0, 0, 0, 0, 0, 0, 0, 0]
        #return False
    else:
        data_list += parse_data(read_buffer)
    
    # print("check 1")
    read_buffer = read_file(yesterday_path)
    if len(read_buffer) == 0:
        data_list += [0, 0, 0, 0, 0, 0, 0, 0]
        #return False
    else:
        data_list += parse_data(read_buffer)

    # print("check 2")
    read_buffer = read_file(today_path)
    if len(read_buffer) == 0:
        data_list += [0, 0, 0, 0, 0, 0, 0, 0]
        #return False
    else:
        temp = parse_data(read_buffer, target_date_check)

        if len(temp) == 0:
            temp = [0, 0, 0, 0, 0, 0, 0, 0]
            #return False

        data_list += temp

    # print("check 3")
    # data_list += parse_data(read_file(before_yesterday_path))
    # data_list += parse_data(read_file(yesterday_path))
    # data_list += parse_data(read_file(today_path))

    data_color_list = make_data_color(data_list)

    x_axis_ticks_label = make_date_tick(today.strftime("%Y-%m-%d"))

    # 600
    fig, ax1 = plt.subplots(1,1, figsize=(6,5), dpi = 100)
    fig.subplots_adjust(bottom=0.14, top=0.9)

    ax2 = ax1.twinx()

    mpl.rcParams["font.size"] = 8
    mpl.rcParams["font.stretch"] = 0

    ax1.set_ylim(0, 9)
    ax1.set_xlim(-0.5, 23.5)
    ax1.tick_params(axis="y", direction="in", which="major", left=True, right=True, top=False, bottom=False, length=4)
    ax1.tick_params(axis="x", direction="in", which="both", left=True, right=True, top=False, bottom=False)

    ax1.set_yticks([0,1,2,3,4,5,6,7,8,9], minor=False)
    ax1.set_xticks([-0.5, 7.5, 15.5, 23.5], minor=False)
    ax1.set_yticklabels([0,1,2,3,4,5,6,7,8,9], x=-0.02, size=8)
    ax1.set_xticklabels(x_axis_ticks_label, y=-0.02, size=8, stretch=0)
    ax1.grid(axis="x", linestyle="--", color="black")

    ax2.set_ylim(0, 9)
    ax2.tick_params(axis="y", direction="in", which="major", left=False, right=False, top=False, bottom=False)
    ax2.set_yticks([5,6,7,8,9], minor=False)
    ax2.set_yticklabels(["G1", "G2", "G3", "G4", "G5"], x=1.01, size=9)

    ax1.set_title("Estimated Planetary K-index (3 hours)", x=0.5, y=1.03)
    ax1.set_ylabel("Kp-index", labelpad=15)

    now_date = datetime.datetime.utcnow()
    ax1.text(0.125, 0.015,
        "Updated {} [UTC]\nKorea Astronomy and Space Science Institute / Space Weather Research Center".format(now_date.strftime("%Y %b %d %H:%M:%S")),
        transform=plt.gcf().transFigure,
        linespacing=1.75)

    ax1.text(1.085, 0.35, "K<4", {"color":"green", "fontsize":9}, rotation=90, transform=plt.gca().transAxes)
    ax1.text(1.085, 0.48, "K=4", {"color":"#d6ca1a", "fontsize":9}, rotation=90, transform=plt.gca().transAxes)
    ax1.text(1.085, 0.61, "K>4", {"color":"red", "fontsize":9}, rotation=90, transform=plt.gca().transAxes)

    ax1.bar(np.arange(len(data_list)), data_list, color=data_color_list, width=0.85)
    
    plt.savefig(image_root_path + today.strftime("/%Y/%Y%m/sec_kpindex_600_%Y%m%d.png"), dpi=100)
    plt.close()

    # 400
    fig, ax1 = plt.subplots(1,1, figsize=(4,1.5), dpi = 100)
    fig.subplots_adjust(bottom=0.12, top=0.89)

    ax2 = ax1.twinx()

    mpl.rcParams["font.size"] = 8
    mpl.rcParams["font.stretch"] = 0

    ax1.set_ylim(0, 9)
    ax1.set_xlim(-0.5, 23.5)
    ax1.tick_params(axis="y", direction="in", which="major", left=True, right=True, top=False, bottom=False, length=4)
    ax1.tick_params(axis="x", direction="in", which="both", left=True, right=True, top=False, bottom=False)

    ax1.set_yticks([0,1,2,3,4,5,6,7,8,9], minor=False)
    ax1.set_xticks([-0.5, 7.5, 15.5, 23.5], minor=False)
    ax1.set_yticklabels([0,1,2,3,4,5,6,7,8,9], x=-0.003, size=6)
    ax1.set_xticklabels(x_axis_ticks_label, size=8)
    ax1.grid(axis="x", linestyle="--", color="black")

    ax2.set_ylim(0, 9)
    ax2.tick_params(axis="y", direction="in", which="major", left=False, right=False, top=False, bottom=False)
    ax2.set_yticks([5,6,7,8,9], minor=False)
    ax2.set_yticklabels(["G1", "G2", "G3", "G4", "G5"], size=7)

    ax1.set_title("Estimated Planetary K-index (3 hours)", x=0.5, y=0.97, size=8)
    ax1.set_ylabel("Kp-index", labelpad=10, size=10)

    ax1.text(1.08, 0.15, "K<4", {"color":"green", "fontsize":9}, rotation=90, transform=plt.gca().transAxes)
    ax1.text(1.08, 0.45, "K=4", {"color":"#d6ca1a", "fontsize":9}, rotation=90, transform=plt.gca().transAxes)
    ax1.text(1.08, 0.75, "K>4", {"color":"red", "fontsize":9}, rotation=90, transform=plt.gca().transAxes)

    ax1.bar(np.arange(len(data_list)), data_list, color=data_color_list, width=0.85)
    
    plt.savefig(image_root_path + today.strftime("/%Y/%Y%m/sec_kpindex_400_%Y%m%d.png"), dpi=100)
    plt.close()

    return True

make_image()
while True:
    # 
    # test
    make_yesterday = True
    make_check = False

    datetime_now = datetime.datetime.utcnow()
    print(datetime_now.isoformat())
    if datetime_now.strftime("%H%M") == "0000":
        make_yesterday = True

    if (datetime_now.strftime("%M") in ["00", "10", "20", "30", "40", "50"]):
        if make_yesterday == True:
            yesterday = datetime_now - datetime.timedelta(days=1)
            make_check = make_image(yesterday.strftime("%Y-%m-%d"))
            if make_check == True:
                make_yesterday = False
            else:
                print("%s | The data is incomplete.\n"%(datetime_now.isoformat()))

        make_image()
        time.sleep(60)
    else:
        time.sleep(30)
