import traceback
from concurrent.futures.thread import ThreadPoolExecutor
import json
import time

from django.http import HttpResponse, JsonResponse

from server import g
from server.models import *


class Report:
    u = None
    roomid = []
    time = None
    use_times = 0
    fre_temp = []
    fre_speed = []
    tar_times = 0
    dispatch_times = []
    details_times = []
    sumcost = []
    change_speed_times = []
    change_temp_times = []


report = Report()


def DailyReport():
    count = 0
    request_list = Request.objects.all()

    user_list = User.objects.all()
    rm_list = []
    temp_list = []
    speed_list = []
    for x in user_list:
        if x.tar_temp == x.cur_temp:
            count = count + 1
    report.tar_times = count  # 达到目标温度次数
    # 详单次数

    count = 0
    y = 0
    # 提出roomid列表
    while (y < len(request_list)):

        for x in request_list:
            if rm_list.count(x.roomid) == 0:
                rm_list.append(x.roomid)
                break
        y = y + 1

    # 费用，详单次数
    y = 0
    while (y < len(rm_list)):

        report.sumcost.append(User.objects.get(roomid=rm_list[y]).cost)
        cur = Request.objects.filter(roomid=rm_list[y])
        report.details_times.append(len(cur))
        y = y + 1

    # 查找最常用温度和风速
    y = 0
    while (y < len(rm_list)):
        rmid = rm_list[y]

        for x in request_list:
            if x.roomid == rmid and x.speed == -1:
                temp_list.append(x)
            elif x.roomid == rmid and x.temp == -1:
                speed_list.append(x)


        z = 0
        t = []
        while (z < len(temp_list) - 1):

            a = temp_list[z]
            b = temp_list[z + 1]
            c = time.mktime(b.time.timetuple())-time.mktime(a.time.timetuple())
            t.append(c)


            z = z + 1
        c = time.time() - time.mktime(temp_list[0].time.timetuple())
        t.append(c)
        t_max = max(t)
        posi = t.index(t_max)
        report.fre_temp.append(temp_list[posi].temp)  # 最常用温度

        z = 0
        t = []
        while (z < len(speed_list) - 1):

            a = speed_list[z]
            b = speed_list[z + 1]

            c = time.mktime(b.time.timetuple())-time.mktime(a.time.timetuple())
            t.append(c)

            z = z + 1
        c = time.time() - time.mktime(speed_list[0].time.timetuple())
        t.append(c)
        t_max = max(t)
        posi = t.index(t_max)
        report.fre_speed.append(speed_list[posi].speed)  # 最常用fs
        y = y + 1

    #温度风速变化次数
    y = 0

    while (y < len(rm_list)):
        sp_count = 0
        te_count = 0
        rmid = rm_list[y]
        for x in request_list:
            if x.roomid == rmid and x.speed == -1:
                sp_count = sp_count + 1
            elif x.roomid == rmid and x.temp == -1:
                te_count = te_count + 1
        report.change_temp_times.append(te_count)
        report.change_speed_times.append(sp_count)
        y = y + 1


    y = 0
    while (y < len(rm_list)):
        daily_report=dailyreport.objects.get(roomid=rm_list[y])
        daily_report.sumcost=report.sumcost[y]
        daily_report.details_times = report.details_times[y]
        daily_report.fre_speed = report.fre_speed[y]
        daily_report.fre_temp = report.fre_temp[y]
        daily_report.change_speed_times = report.change_speed_times[y]
        daily_report.change_temp_times = report.change_temp_times[y]
        daily_report.save()
        y = y + 1

