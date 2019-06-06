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

    print("b")

    u = User.objects.get(roomid="qwe")
    g["test"] = "test123"
    g["User"] = u
    # 先隔出一秒打印出a，再过一秒打出b

    tb = threading.Thread(target=testb)

    print("DONE")
    print(g)
    print(g["User"].roomid)
