from concurrent.futures.thread import ThreadPoolExecutor
import json
import time

from django.forms import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

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
        self.cur_feeRate = self.feeRate_M  # 默认设置初始费率为中等
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
        duration = 3
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
            print("----------关机调度------------")
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
        # 当某个空调到达设定温度后，状态为被挂起，放入等待队列
        elif self.instance.state == 2 and self.find_repeat(self.instance, self.serviceQueue) == 1:
            print("----------达到设定温度调度------------")

            temp = self.return_repeat(self.instance, self.serviceQueue)
            self.serviceQueue.remove(temp)

            u = User.objects.get(roomid=temp.roomid)
            u.wait_time = 60
            u.speed = 0
            u.save()
            self.waitQueue.append(u)
        # 判断是否是新的空调开机(此时服务队列未满
        elif len(self.serviceQueue) < self.handleNum and self.find_repeat(self.instance, self.serviceQueue) == 0:
            print("----------新空调开机调度，服务队列未满------------")
            # 若是达到了目标温度的空调再次加入服务，则需要将其从等待队列删除
            if self.find_repeat(self.instance, self.waitQueue) == 1:
                self.waitQueue.remove(self.return_repeat(self.instance, self.waitQueue))
            self.serviceQueue.append(self.instance)
            self.state_time = 0  # 服务状态变化
            self.instance.state = 1
        # 判断是否是新的空调开机(此时服务队列已满
        elif self.find_repeat(self.instance, self.waitQueue) == 0 and self.find_repeat(self.instance,
                                                                                       self.serviceQueue) == 0:
            print("----------新空调开机调度，服务队列满了------------")

            self.instance.wait_time = 16
            self.instance.state = 2
            self.waitQueue.append(self.instance)  # 放入等待队列
        # 其他的情况就是服务或是等待队列中的从机风速发生变化,或者时间片调度
        else:
            for x in self.serviceQueue:
                if self.instance.speed > x.speed:
                    count = count + 1
            if count == 1:
                print("----------只比一个风速大------------")
                max_temp = self.serviceQueue[self.find_max_sp()]

                self.serviceQueue.remove(max_temp)
                max = User.objects.get(roomid=max_temp.roomid)
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
                print("----------比多个风速大------------")
                x = 0
                while x < self.handleNum - 1:
                    if self.serviceQueue[x].speed == self.serviceQueue[x + 1].speed:
                        speed_equal = speed_equal + 1
                    x += 1
                if speed_equal == 0:  # 没有风速相等的

                    min_temp = self.serviceQueue[self.find_min()]
                    self.serviceQueue.remove(min_temp)
                    min = User.objects.get(roomid=min_temp.roomid)
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
                    print("----------比所有的风速都小------------")
                    temp_max = self.serviceQueue[self.find_max()]
                    self.serviceQueue.remove(temp_max)
                    max = User.objects.get(roomid=temp_max.roomid)
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
                print("----------时间片调度------------")
                # 启动时间片调度
                # if 两分钟没有状态变化
                # 取出服务队列中服务时长最长的，将风速置为(0)，状态置为被挂起(2)，放入等待队列
                # 再将等待时间最长的状态置为开启，放入服务队列
                for x in self.waitQueue:
                    if x.wait_time == 0:
                        # 若服务队列中有对象
                        if (len(self.serviceQueue) != 0):
                            temp_max = self.serviceQueue[self.find_max()]
                            self.serviceQueue.remove(temp_max)

                            max = User.objects.get(roomid=temp_max.roomid)
                            max.wait_time = 40
                            max.state = 2
                            max.speed = 0
                            max.save()
                            self.waitQueue.append(max)

                        x_temp = User.objects.get(roomid=x.roomid)
                        x_temp.state = 1
                        x_temp.wait_time = 40
                        x_temp.serve_time = 0
                        temp = self.return_repeat(x_temp, self.waitQueue)
                        self.waitQueue.remove(temp)
                        self.serviceQueue.append(x_temp)  # 进入服务队列

                        self.state_time = 0  # 服务状态变化
                        x_temp.save()
                        # 这里是因为时间片调度不需要保存instance
                        save_instance = 0

                        break
        if save_instance:
            self.instance.save()
        print("服务队列：", end=' ')
        for x in self.serviceQueue:
            print(x.roomid, end=',')
        print("等待队列：", end=' ')
        for x in self.waitQueue:
            print(x.roomid, end=',')
        print(" ###########   ")

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

        if self.status == 1:
            for x in self.waitQueue:
                y = User.objects.get(roomid=x.roomid)

                y.wait_time -= duration
                if y.wait_time < 0: y.wait_time = 0
                x.wait_time = y.wait_time
                print(str(x.roomid) + " wait_time=" + str(x.wait_time))

                y.save()
                if x.wait_time == 0:
                    self.instance = y

                    daily_temp = dailyreport.objects.get(roomid=y.roomid)
                    daily_temp.dispatch_times += 1
                    daily_temp.save()

                    self.Dispatch()

            for x in self.serviceQueue:
                y = User.objects.get(roomid=x.roomid)
                y.serve_time += duration
                x.serve_time = y.serve_time
                print(str(x.roomid) + " serve_time=" + str(x.serve_time))
                y.save()
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
    return render(request, "lcmanager.html")


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


@csrf_exempt
def setPara(request):
    if request.method == 'POST':
        # print(request.POST['handleNum'])
        g['handleNum'] = request.POST['handleNum']
        g['default_temp'] = request.POST['defaultTemp']
        g['mode'] = request.POST['mode']
        feerate = request.POST['feerate']
        if feerate == '1':
            m.cur_feeRate = g['feeRate_L']
        elif feerate == '2':
            m.cur_feeRate = g['feeRate_M']
        else:
            m.cur_feeRate = g['feeRate_H']

        return JsonResponse({"content": "修改成功！"})


def checkMyState(request):
    if m.cur_feeRate == g['feeRate_L']:
        feerate = 1
    elif m.cur_feeRate == g['feeRate_M']:
        feerate = 2
    else:
        feerate = 3
    data = {"status": m.status,
            "mode": int(g['mode']),
            "defaultTemp": int(g['default_temp']),
            "feerate": feerate,
            "handleNum": int(g['handleNum']), }
    return JsonResponse(data)


def checkState(request):
    userList = User.objects.all()
    data = {}
    list = []
    son = {'roomid': '',
           'state': 0,
           'cur_temp': 0,
           'tar_temp': 0,
           'speed': 0,
           'cost': 0,
           'serve_time': 0, }
    for u in userList:

        son['roomid'] = u.roomid
        if u.state == 0:
            state = "关机"
        elif u.state == 2:
            state = "暂时挂起"
        else:
            state = "运行中"
        son['state'] = state
        son['cur_temp'] = u.cur_temp
        son['tar_temp'] = u.tar_temp
        son['speed'] = u.speed
        son['cost'] = u.cost
        son['serve_time'] = u.serve_time
        son_copy = son.copy()
        list.append(son_copy)

    data['items'] = list
    return JsonResponse(data)
