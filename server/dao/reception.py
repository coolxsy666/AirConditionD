from concurrent.futures.thread import ThreadPoolExecutor
import json
import datetime

from django.http import HttpResponse, JsonResponse

from server import g
from server.models import *


class RDR:
    id = []
    type = []
    time = []
    cost = []
    data = []


r = RDR()


# 创建详单
def CreatRDR(RoomId):
    rdr_list = Request.objects.filter(roomid=RoomId)
    x = 1
    for y in rdr_list:
        r.id.append(x)
        if y.temp == -1:
            r.type.append('SpeedChange')
            r.data.append(y.speed)
        else:
            r.type.append('TempChange')
            r.data.append(y.temp)
        r.time.append(y.time)
        r.cost.append(y.cost)
        x = x + 1

    return r


# 打印详单
def PrintRDR(RoomId):
    full_path = 'RDRs/'+RoomId + '_RDR' + '.txt'
    file = open(full_path, 'w')
    x = 0

    for x in range(1, len(r.id)):
        file.write('序号'+str(r.id[x]) + ' 请求类型' + str(r.type[x]) +
                   ' 请求数据' + str(r.data[x]) + ' 请求时间' + str(r.time[x]) +
                   ' 截止费用' + str(r.cost[x]) + '\n')

    file.close()


# 出账单
def CreatInvoice(RoomId):
    cost = User.objects.filter(roomid=RoomId)
    return cost


# 打印账单
def PrintInvoice(RoomId):
    cost = User.objects.filter(roomid=RoomId)
    full_path = RoomId + 'Invoice' + '.txt'
    file = open(full_path, 'w')
    file.write(cost.id + ' ' + cost.roomid + ' ' + cost.cost + '\n')
    file.close()
