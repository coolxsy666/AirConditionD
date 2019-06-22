import threading
import time

from django.views.decorators.csrf import csrf_exempt

from . import g
from django.shortcuts import render
from server.dao.master import m
from server.models import User, dailyreport, Request
from server.dao.manager import *
from server.dao.slave import *
from server.dao.reception import *
# Create your views here.
from django.http import HttpResponse, JsonResponse


def index(request):
    return render(request, 'test.html')


def choose(request):
    return render(request, "choose.html")


def customer_login(request):
    return render(request, "customerlogin.html")


def front(request):
    return render(request, "front.html")


def manager(request):
    return render(request, "manager.html")


@csrf_exempt
def root_login(request):
    if (request.method == 'POST'):
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == "front" and password == "123456":
            return render(request, "front.html")
        elif username == "lcmanager" and password == "123456":
            return render(request, "lcmanager.html")
        elif username == "manager" and password == "123456":
            return render(request, "manager.html")
    else:
        return render(request, "login.html")


@csrf_exempt
def login_customer(request):
    if request.method == 'POST':
        room_id = request.POST['room_id']
        return render(request, "customer.html", {'room_id': room_id})


# --------------------------经理-------------------------------
# queryReport(request, id):查看日报表
# ------------------------------------------------------------
def queryReport(request):
    DailyReport()
    userList = dailyreport.objects.all()
    data = {}
    list = []
    son = {'roomid': '',
           'use_times': 0,
           'fre_temp': 0,
           'fre_speed': 0,
           'dispath_times': 0,
           'details_times': 0,
           'change_temp_times': 0,
           'change_speed_times': 0,
           'sumcost': 0, }
    for u in userList:
        son['roomid'] = u.roomid

        son['use_times'] = u.use_times
        son['fre_temp'] = u.fre_temp
        son['fre_speed'] = u.fre_speed
        son['dispatch_times'] = u.dispatch_times
        son['details_times'] = u.details_times
        son['change_temp_times'] = u.change_temp_times
        son['change_speed_times'] = u.change_speed_times
        son['sumcost'] = u.sumcost
        son_copy = son.copy()
        list.append(son_copy)

    data['items'] = list
    return JsonResponse(data)


# ---------------------------前台------------------------------
# printSpec(request, roomid):打印详单
# printBill(request, roomid):打印账单
# -------------------------------------------------------------
def quitroom(requesty, roomid):
    u = User.objects.get(roomid=roomid)
    u.state = 0
    u.speed = 0
    u.save()

    # m.setInstance(u)
    # m.Dispatch()

    for x in slaves:
        if x.roomid == roomid:
            x.logout = 1

            break

    r = dailyreport.objects.get(roomid=roomid)
    r.use_times += 1
    r.save()

    details = CreatRDR(roomid)
    PrintRDR(roomid)
    requestList = Request.objects.filter(roomid=roomid)

    data = {}
    list = []
    list_cost = []
    son = {'id': 0,
           'type': 0,
           'data': 0,
           'time': '',
           'cost': 0, }
    son_cost = {
        'roomid': '',
        'cost': 0,
        'checkIn': '',
        'checkOut': '',
    }
    son_cost['roomid'] = roomid
    son_cost['cost'] = u.cost
    son_cost['checkIn'] = dailyreport.objects.get(roomid=roomid).time
    son_cost['checkOut'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    son_cost_copy = son_cost.copy()
    list_cost.append(son_cost_copy)
    for x in range(1, len(requestList)):
        son['id'] = details.id[x]
        son['type'] = details.type[x]
        son['time'] = details.time[x]
        son['data'] = details.data[x]
        son['cost'] = details.cost[x]

        son_copy = son.copy()
        list.append(son_copy)

    data['items'] = list
    data['invoice'] = list_cost
    return JsonResponse(data)


def printReport(request):
    full_path = str(time.strftime("%Y-%m-%d", time.localtime())) + '.txt'
    file = open(full_path, 'w')

    for x in dailyreport.objects.all():
        file.write('\n\n房间号:' + str(x.roomid) +
                   '\n{\n' + '   住房日期:' + str(x.time) +
                   '\n   使用空调次数:' + str(x.use_times) + '\n   最常用风速:' + str(x.fre_speed) +
                   '\n   最常用温度:' + str(x.fre_temp) + '\n   被调度次数:' + str(x.dispatch_times) + '\n   详单数:' +
                   str(x.details_times) + '\n   调温次数:' + str(x.change_temp_times) + '\n   调风次数:' +
                   str(x.change_speed_times) + '\n   总计花费:' + str(x.sumcost) + '\n}\n')

    file.close()
    return HttpResponse(200)


def printBill(request, roomid):
    pass


# 测试
def test(request, op, id):
    if request.method == "GET":
        print("op=" + str(op) + "   id=" + str(id))
    return HttpResponse("slave")


def testb(request):
    return JsonResponse({"content": "conweornwontowptgphgpehgperthpv23"})
