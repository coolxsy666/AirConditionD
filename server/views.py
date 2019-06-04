import threading
import time
from . import g
from django.shortcuts import render
from server.models import User, dailyreport, Request
from server.dao import master
# Create your views here.
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


# --------------------从控机------------------------------
# 操作
# slave(request, roomid):从机主页信息
# login(request, username):
# tempControl(request, op, roomid):温度控制
# speedControl(request, op, roomid):风速控制
# turnOn(request, roomid):从控机开机
# turnOff(request, roomid):从控机关机
# -------------------------------------------------------
# 从机主页信息
def slave(request, roomid):
    try:

        u = User.objects.get(roomid=roomid)

        return render(request, 'index.html', {"test_str": "roomid=" + u.roomid +
                                                          "\ntarget_temp=" + str(u.tar_temp) +
                                                          "\ncur_temp=" + str(u.cur_temp) +
                                                          "\nspeed=" + str(u.speed) +
                                                          "\ncost=" + str(u.cost)})
    except:
        return HttpResponse("gg", 404)


# 登录注册客户信息
def login(request, username):
    u = User(roomid=username, cur_temp=g["default_temp"], tar_temp=g["default_temp"])
    u.save()
    return render(request, 'index.html', {"test_str": username})


def tempControl(request, op, roomid):
    try:
        u = User.objects.get(roomid=roomid)

        if op == "high":
            u.tar_temp += 1
            u.save()
            r = Request(roomid=roomid, temp=u.tar_temp, time=time.time())
            r.save()
            return render(request, 'index.html', {"test_str": "目标温度改变“”"})
        elif op == "low":
            u.tar_temp -= 1
            u.save()
            r = Request(roomid=roomid, temp=u.tar_temp, time=time.time())
            r.save()
            return render(request, 'index.html', {"test_str": "目标温度改变“”"})
        else:
            return HttpResponse("wrong!!!please check url!", 404)
    except:
        return HttpResponse("gg", 404)


def speedControl(request, op, roomid):
    try:
        u = User.objects.get(roomid=roomid)

        if op == "high":
            r = Request(roomid=roomid, speed=u.speed + 1, time=time.time())
            r.save()
            return render(request, 'index.html', {"test_str": "目标风速改变请求加入队列“”"})
        elif op == "low":
            r = Request(roomid=roomid, speed=u.speed - 1, time=time.time())
            r.save()
            return render(request, 'index.html', {"test_str": "目标风速改变请求加入队列“”"})
        else:
            return HttpResponse("wrong!!!please check url!", 404)
    except:
        return HttpResponse("gg", 404)
    pass


# 从控机开机
def turnOn(request, roomid):
    try:
        u = User.objects.get(roomid=roomid)
        u.state = 1
        return render(request, 'index.html', {"test_str": "成功开启！"})
    except:
        return HttpResponse("turn on false!", 404)


# 从控机关机
def turnOff(request, roomid):
    try:
        u = User.objects.get(roomid=roomid)
        u.state = 0
        return render(request, 'index.html', {"test_str": "成功开启！"})
    except:
        return HttpResponse("turn on false!", 404)


# --------------------------- 空调管理员------------------------------------
# master(request):查看主控机主页
# startUP(request):开启主控机
# closeUp(request):关闭主控机
# editSlave(request):修改从控机参数
# setPara(request):设置默认参数
# checkState(request):查看从控机信息
# --------------------------------------------------------------------------
def master(request):
    return HttpResponse("master")


def startUP(request):
    pass


def closeUp(request):
    pass


def editSlave(request):
    pass


def setPara(request):
    pass


def checkState(request):
    pass


# --------------------------经理-------------------------------
# queryReport(request, id):查看日报表
# ------------------------------------------------------------
def queryReport(request, id):
    pass


# ---------------------------前台------------------------------
# printSpec(request, roomid):打印详单
# printBill(request, roomid):打印账单
# -------------------------------------------------------------
def printSpec(request, roomid):
    pass


def printBill(request, roomid):
    pass


# 测试
def test(request, op, id):
    if request.method == "GET":
        print("op=" + str(op) + "   id=" + str(id))
    return HttpResponse("slave")


def testb(request):
    sleep(1)
    print("b")

    u = User.objects.get(roomid="qwe")
    g["test"] = "test123"
    g["User"] = u
    # 先隔出一秒打印出a，再过一秒打出b

    tb = threading.Thread(target=testb)

    print("DONE")
    print(g)
    print(g["User"].roomid)
