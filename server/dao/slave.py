import math
import time
import datetime
from concurrent.futures import ThreadPoolExecutor

from django.http import HttpResponse
from django.shortcuts import render
from server import *

from server.models import *
from .master import m


# 从控机
class Slave:
    u = None
    roomid = None
    state = 0  # 运行状态 为1则处于运行状态 为2则被挂起
    logout = 0  # 若用户退出系统，则logout为1

    cur_temp = 0
    tar_temp = 0
    out_temp = 0
    speed = 0
    cost = 0  # 当前总计花费

    frequency = 3  # 温度更新时间频率
    rate = 0.1  # 温度随风速改变速率
    startTime = 0  # 启动时间
    time = 0

    # 从机初始化
    def init(self, roomid, out_temp):
        self.logout = 0
        self.u = User.objects.get(roomid=roomid)

        self.out_temp = out_temp
        self.cur_temp = self.u.cur_temp
        self.tar_temp = self.u.tar_temp
        self.update()
        self.startTime = time.time()
        self.time = time.time()

    # 更新用户调制的信息
    def syntax(self):
        self.u = User.objects.get(roomid=self.u.roomid)
        self.tar_temp = self.u.tar_temp

        # print(self.u.is_suspended,self.u.state)
        self.speed = self.u.speed

    # 若目标温度已到达，则风速降为0
    def update(self):
        self.u.cur_temp = round(self.cur_temp)
        self.u.cost = self.cost
        # if self.cur_temp == self.tar_temp: self.u.speed = 0因为到达目标温度之后改为风速不变，所以先去掉这条
        self.u.save()

    def run(self):

        while self.logout != 1:
            during_time = time.time() - self.time
            if during_time > (self.frequency - 1e-4):
                self.syntax()
                if self.u.state == 1 and self.u.speed != 0:

                    a = self.speed * self.rate * during_time  # 温度变化参数
                    self.cost += m.cur_feeRate / 100.0 * self.speed
                    if self.tar_temp > self.cur_temp:

                        self.cur_temp = min(float(self.cur_temp) + a,
                                            float(self.tar_temp))

                    elif self.tar_temp < self.cur_temp:

                        self.cur_temp = max(float(self.cur_temp) - a,
                                            float(self.tar_temp))
                    elif round(self.tar_temp) == round(self.cur_temp):
                        self.cur_temp = round(self.cur_temp)
                    print("房间：" + str(self.u.roomid) + " 风速为" + str(self.speed)
                          + " 当前温度为" + str(self.cur_temp)
                          + " 当前花费为" + str(self.cost)
                          + " 时间：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    # 风速为零，当前温度不等于外部温度,且当前状态为挂起或者关闭
                elif (self.u.state == 2 or self.u.state == 0) and self.cur_temp != self.out_temp and self.u.speed == 0:
                    a = self.rate / 2
                    if self.out_temp > self.cur_temp:
                        self.cur_temp = min(float(self.cur_temp) + a,
                                            float(self.out_temp))
                    if self.out_temp < self.cur_temp:
                        self.cur_temp = max(float(self.cur_temp) - a,
                                            float(self.out_temp))
                    print("房间：" + str(self.u.roomid) + "无风速，当前温度为" + str(self.cur_temp)
                          + " 当前花费为" + str(self.cost)
                          + " 时间：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    # if self.switch:
                    #     if (abs(self.cur_temp - self.tar_temp) > 1
                    #             and time.time() - self.last_req > 1):
                    #         self.last_req = time.time()
                    #         self.request()

                # elif self.cur_temp == self.out_temp and self.switch:
                #     if time.time() - self.last_req > 1:
                #         self.last_req = time.time()
                #         self.request()

                self.time = time.time()
                self.update()

    # 将用户请求加入队列
    def push(self):
        pass

    # 获取服务队列
    def getServiceQueue(self):
        pass

    # 获取等待队列
    def getWaitQueue(self):
        pass

    # 处理用户请求
    def doJob(self):
        pass


executor = ThreadPoolExecutor(max_workers=16)


# --------------------从控机------------------------------
# 操作
# slave(request, roomid):从机主页信息
# login(request, username):用户登录，同时从机初始化
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
    try:
        u = User.objects.get(roomid=username)
        return HttpResponse("注册失败，用户名重复！")
    except:
        u = User(roomid=username, cur_temp=g["default_temp"], tar_temp=g["default_temp"])
        u.save()
        r = dailyreport(roomid=username)
        r.save()
        # slave = Slave()
        # slave.init(username, g["default_temp"])
        # executor.submit(slave.run)

        return HttpResponse("注册成功")


# 从控机开机
def turnOn(request, roomid):

    u = User.objects.get(roomid=roomid)
    slave = Slave()
    slave.init(roomid, g["default_temp"])
    executor.submit(slave.run)
    if u.state==0:
        u.state = 2
        u.save()
        # t=Request.objects.filter(roomid='12')
        # during=time.time()-time.mktime(t[0].time.timetuple())

        m.instance = u
        m.Dispatch()

        return HttpResponse("开启")

    return HttpResponse("开机失败")
# 从控机关机
def turnOff(request, roomid):
    try:
        u = User.objects.get(roomid=roomid)
        u.state = 0
        u.save()
        r = dailyreport.objects.get(roomid=roomid)
        r.use_times += 1
        r.save()
        return HttpResponse("关机成功")
    except:
        return HttpResponse("turn on false!", 404)


def tempControl(request, op, roomid):
    try:
        u = User.objects.get(roomid=roomid)

        if op == "high":
            u.tar_temp = u.tar_temp + 1
            u.save()
            r = Request(roomid=roomid, temp=u.tar_temp, speed=u.speed, time=time.time())
            r.save()
            return HttpResponse("温度升高！")
        elif op == "low":
            u.tar_temp -= 1
            u.save()
            r = Request(roomid=roomid, temp=u.tar_temp, speed=u.speed, time=time.time())
            r.save()
            return HttpResponse("温度降低")
        else:
            return HttpResponse("wrong!!!please check url!", 404)
    except:
        return HttpResponse("gg", 404)


def speedControl(request, op, roomid):
    try:
        u = User.objects.get(roomid=roomid)

        if op == "high":
            r = Request(roomid=roomid, temp=u.cur_temp, speed=u.speed + 1, time=time.time())
            r.save()

            if m.waitQueue.count(u) != 0:
                u.speed += 1
                m.instance = u
                m.Dispatch()
            else:
                u.speed += 1
                u.save()
            return HttpResponse("风速升高")
        elif op == "low":
            r = Request(roomid=roomid, temp=u.cur_temp, speed=u.speed - 1, time=time.time())
            r.save()
            m.instance = u
            if m.waitQueue.count(u) != 0:
                m.Dispatch()
            else:
                u.speed -= 1
                u.save()
            return HttpResponse("风速降低")
        else:
            return HttpResponse("wrong!!!please check url!", 404)
    except:
        return HttpResponse("gg", 404)
