from concurrent.futures.thread import ThreadPoolExecutor
import json
import time

from django.http import HttpResponse, JsonResponse

from server import g
from server.models import *


# 主控机
class Master:
    status = 0  # 运行状态 为1则处于运行状态
    mode = 0  # 制冷制热模式 制冷为0 制热为1
    temp_highLimit = 0  # 温度限制
    temp_lowLimit = 0
    default_temp = 0
    cur_feeRate = 0
    feeRate_H = 0,  # 费率计算参数
    feeRate_M = 0,
    feeRate_L = 0,
    handleNum = 0  # 每秒最多处理请求数目，默认为3条

    serviceQueue = []
    waitQueue = []

    state_time = 0  # 无服务状态变化持续时间
    instance = None

    last_time = 0  # 用来刷新队列时间信息

    def init(self):
        self.mode = g["mode"]
        self.default_temp = g["default_temp"]  # 初始外界温度以及空调初始设置温度
        self.temp_highLimit = g["temp_highLimit"]
        self.temp_lowLimit = g["temp_lowLimit"]
        self.feeRate_H = g["feeRate_H"]
        self.feeRate_M = g["feeRate_M"]
        self.feeRate_L = g["feeRate_L"]
        self.handleNum = g["handleNum"]
        self.cur_feeRate = self.feeRate_M  # 设置初始费率为中等
        self.last_time = 0
        # 删除所有请求
        Request.objects.all().delete()
        # 重置所有房间初始信息
        for item in User.objects.all():
            # if self.mode == 0:
            item.speed = 0
            item.state = 0
            item.cur_temp = item.tar_temp = self.default_temp
            item.is_suspended = 0
            item.serve_time = 0
            item.wait_time = 0
            item.save()

    def run(self):
        duration = 2
        while (True):
            if not self.status: continue
            if time.time() - self.last_time > duration:
                self.fresh(duration)
                self.last_time = time.time()

    def turnoffSlaves(self):
        for item in User.objects.all():
            item.state = 0
            item.speed = 0
            item.save()

    # 将用户请求加入队列
    def push(self):
        pass

    # 获取服务队列
    def getServiceQueue(self):
        pass

    # 获取等待队列
    def getWaitQueue(self):
        pass

        # 调度函数

        # 调度函数

    def Dispatch(self):
        count = 0
        save_instance = 1  # 是否需要保存instance
        speed_equal = 0
        # 状态判断
        if self.instance.state == 0:
            # 从控机关机，查找在哪个队列里
            self.state_time = 0  # 服务状态变化
            # 如果不在等待队列里
            if self.find_repeat(self.instance, self.waitQueue) == 0:
                temp = self.return_repeat(self.instance, self.serviceQueue)
                self.serviceQueue.remove(temp)
            # 如果不在服务队列里
            elif self.find_repeat(self.instance, self.serviceQueue) == 0:
                temp = self.return_repeat(self.instance, self.waitQueue)
                self.waitQueue.remove(temp)
            else:
                print("!!!!!!!!!!!!!!!!从控机关机，服务等待队列中都找不到此从机")
        # 判断是否是新的空调开机(此时服务队列未满
        elif len(self.serviceQueue) < self.handleNum and self.find_repeat(self.instance,
                                                                          self.serviceQueue) == 0:
            self.serviceQueue.append(self.instance)
            self.state_time = 0  # 服务状态变化
            self.instance.state = 1
        # 判断是否是新的空调开机(此时服务队列已满
        elif self.find_repeat(self.instance, self.waitQueue) == 0 and self.find_repeat(self.instance,
                                                                                       self.serviceQueue) == 0:
            self.instance.wait_time = 16
            self.instance.state = 2
            self.waitQueue.append(self.instance)  # 放入等待队列
        # 其他的情况就是服务或是等待队列中的从机风速发生变化,或者时间片调度
        else:
            for x in self.serviceQueue:
                if self.instance.speed > x.speed:
                    count = count + 1
            if count == 1:

                max = self.serviceQueue[self.find_max_sp()]
                self.serviceQueue.remove(max)
                max.wait_time = 40  # 分配一个等待服务时长
                max.state = 2
                self.waitQueue.append(max)  # 进入等待队列
                max.save()

                self.instance.state = 1
                temp = self.return_repeat(self.instance, self.waitQueue)
                self.waitQueue.remove(temp)
                self.serviceQueue.append(self.instance)
                self.state_time = 0  # 服务状态变化

            elif count > 1:
                x = 0
                while x < self.handleNum - 1:
                    if self.serviceQueue[x].speed == self.serviceQueue[x + 1].speed:
                        speed_equal = speed_equal + 1
                    x += 1
                if speed_equal == 0:  # 没有风速相等的
                    min = self.serviceQueue[self.find_min()]
                    self.serviceQueue.remove(min)
                    min.wait_time = 40  # 分配一个等待服务时长
                    min.state = 2
                    self.waitQueue.append(min)  # 取出服务队列中风速最小的
                    min.save()

                    self.instance.state = 1
                    temp = self.return_repeat(self.instance, self.waitQueue)
                    self.waitQueue.remove(temp)
                    self.serviceQueue.append(self.instance)  # 进入服务队列
                    self.state_time = 0  # 服务状态变化

                else:
                    max = self.serviceQueue[self.find_max()]
                    self.serviceQueue.remove(max)
                    max.wait_time = 40  # 分配一个等待服务时长
                    max.state = 2
                    self.waitQueue.append(max)  # 取出服务队列中服务时长最长的
                    max.save()

                    self.instance.state = 1
                    temp = self.return_repeat(self.instance, self.waitQueue)
                    self.waitQueue.remove(temp)
                    self.serviceQueue.append(self.instance)  # 进入服务队列
                    self.state_time = 0  # 服务状态变化

            elif count == 0:
                # 启动时间片调度
                # if 两分钟没有状态变化
                # 取出服务队列中服务时长最长的，将风速置为(0)，状态置为被挂起(2)，放入等待队列
                # 再将等待时间最长的状态置为开启，放入服务队列
                for x in self.waitQueue:
                    if x.wait_time == 0:
                        max = self.serviceQueue[self.find_max()]
                        max.wait_time = 40

                        max.state = 2
                        max.speed = 0
                        max.save()
                        self.waitQueue.append(max)
                        temp = self.return_repeat(max, self.waitQueue)
                        self.serviceQueue.remove(temp)

                        x.state = 1
                        x.wait_time = 40
                        x.serve_time = 0
                        self.serviceQueue.append(x)  # 进入服务队列
                        temp = self.return_repeat(x, self.waitQueue)
                        self.waitQueue.remove(temp)

                        self.state_time = 0  # 服务状态变化
                        x.save()
                        # 这里是因为时间片调度不需要保存instance
                        save_instance = 0
        if save_instance:
            self.instance.save()
        print("服务队列")
        for x in self.serviceQueue:
            print(x.roomid)
        print("等待队列")
        for x in self.waitQueue:
            print(x.roomid)

    # 一个房间在队列中的属性和数据库中的属性不同，所以要通过获取id值进行队列操作
    # 查找队列中是否存在instance
    def find_repeat(self, instance, queue):
        for x in queue:
            if instance.roomid == x.roomid:
                return 1

        return 0

    # 返回队列中的instance,
    # Attention!要删除队列中某一个对象时要用到此函数
    def return_repeat(self, instance, queue):
        for x in queue:
            if instance.roomid == x.roomid:
                return x
        return 0

    # 返回最小值所在位置
    def find_min(self):
        list = []
        for x in self.serviceQueue:
            list.append(x.speed)

        return list.index(min(list))

    # 返回最大风速所在位置
    def find_max_sp(self):
        list = []
        for x in self.serviceQueue:
            list.append(x.speed)

        return list.index(max(list))

    # 返回服务时长最大值所在位置
    def find_max(self):
        list = []
        for x in self.serviceQueue:
            list.append(x.serve_time)

        return list.index(max(list))

    def setInstance(self, instance):
        self.instance = instance

    def fresh(self, duration):

        for x in self.waitQueue:
            y = User.objects.get(roomid=x.roomid)

            y.wait_time -= duration
            if y.wait_time < 0: y.wait_time = 0
            x.wait_time = y.wait_time
            print(str(x.roomid) + " wait_time=" + str(x.wait_time))

            y.save()
            if x.wait_time == 0:
                self.instance = x
                self.Dispatch()

        for x in self.serviceQueue:

            y = User.objects.get(roomid=x.roomid)
            y.serve_time += duration
            x.serve_time = y.serve_time
            print(str(x.roomid) + " serve_time=" + str(x.serve_time))
            x.save()
        self.state_time += duration
        print("无服务状态变化持续时间state_time=" + str(self.state_time))


m = Master()
executor = ThreadPoolExecutor(max_workers=1)


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
    m.status = 1
    m.init()
    executor.submit(m.run)
    data = {"status:": m.status,
            "mode:": m.mode,
            "temp_highLimit:": m.temp_highLimit,
            "temp_lowLimit:": m.temp_lowLimit,
            "cur_feeRate:": m.cur_feeRate,
            "handleNum:": m.handleNum, }

    return JsonResponse(json.dumps(data), safe=False)


def closeUp(request):
    m.status = 0
    m.turnoffSlaves()
    return HttpResponse("主控机关闭！从控机全部关闭！", 200)


def editSlave(request):
    pass


def setPara(request):
    pass


def checkState(request):
    data = {"status:": m.status,
            "mode:": m.mode,
            "temp_highLimit:": m.temp_highLimit,
            "temp_lowLimit:": m.temp_lowLimit,
            "cur_feeRate:": m.cur_feeRate,
            "handleNum:": m.handleNum, }

    return JsonResponse(json.dumps(data), safe=False)
