import math
import time
from concurrent.futures import ThreadPoolExecutor

from django.http import HttpResponse
from django.shortcuts import render
from server import *

from server.models import *


# 从控机
class Slave:
    u = None
    roomid = None
    state = 0  # 运行状态 为1则处于运行状态
    is_suspended = 0  # 是否被挂起，为1则被挂起

    cur_temp = 0
    tar_temp = 0
    out_temp = 0
    speed = 0
    cost = 0  # 当前总计花费

    frequency = 1  # 温度更新时间频率
    rate = 0.1  # 温度随风速改变速率
    startTime = 0  # 启动时间
    time = 0

    # 从机初始化
    def init(self, roomid, out_temp):
        self.u = User.objects.get(roomid=roomid)

        self.out_temp = self.cur_temp = out_temp
        self.tar_temp = self.u.tar_temp
        self.update()
        self.startTime = time.time()
        self.time = time.time()

    # 更新用户调制的信息
    def syntax(self):
        self.u = User.objects.get(roomid=self.u.roomid)
        self.tar_temp = self.u.tar_temp
        #print(self.u.speed)
        self.speed = self.u.speed

    # 若目标温度已到达，则风速降为0
    def update(self):
        self.u.cur_temp = round(self.cur_temp)
        self.u.is_suspended = self.is_suspended
        if self.cur_temp == self.tar_temp: self.u.speed = 0
        self.u.save()

    def run(self):

        while self.u.state == 1 and self.u.is_suspended == 0:

            # 温度不为零
            if time.time() - self.time > (self.frequency - 1e-4):
                self.syntax()
                if self.speed > 0:
                    a = self.speed * self.rate
                    if self.tar_temp > self.cur_temp:

                        self.cur_temp = min(float(self.cur_temp + a),
                                            float(self.tar_temp))

                    elif self.tar_temp < self.cur_temp:

                        self.cur_temp = max(float(self.cur_temp - a),
                                            float(self.tar_temp))
                    print("房间："+str(self.u.roomid)+"风速为" + str(self.speed) + "当前温度为" + str(self.cur_temp))
                # 风速为零，当前温度不等于外部温度
                elif self.cur_temp != self.out_temp:
                    a = self.rate / 2
                    if self.out_temp > self.cur_temp:
                        self.cur_temp = min(float(self.cur_temp + a),
                                            float(self.tar_temp))
                        print("房间："+str(self.u.roomid)+"无风速，当前温度为" + str(self.cur_temp))
                    if self.out_temp < self.cur_temp:
                        self.cur_temp = max(float(self.cur_temp - a),
                                            float(self.tar_temp))
                        print("房间："+str(self.u.roomid)+"无风速，当前温度为" + str(self.cur_temp))
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
        print("房间"+str(self.u.roomid)+"空调关闭")

        return
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




executor = ThreadPoolExecutor(2)


# 从控机开机
def turnOn(request, roomid):
    try:
        u = User.objects.get(roomid=roomid)
        u.state = 1
        slave = Slave()
        slave.init(roomid, g["default_temp"])
        executor.submit(slave.run)
        return render(request, 'index.html', {"test_str": "成功开启！"})
    except:
        return HttpResponse("turn on false!", 404)
