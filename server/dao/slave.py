import math
import time
import datetime
import traceback
from concurrent.futures import ThreadPoolExecutor

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from server import *

from server.models import *
from .master import m
from .manager import *


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
    energy = 0
    energyRate = 1  # 耗电标准 高风：1度/1分钟 中风：1度/2分钟 低风：1度/3分钟

    frequency = 10  # 温度更新时间频率
    rate = 0.4  # 温度每分钟改变速率，中风0.5 高风多20％ 低风低20％
    shutDownRate = 0.5  # 关机状态下温度每分钟改变速率
    startTime = 0  # 启动时间
    time = 0

    # 从机初始化
    def init(self, roomid, out_temp):
        self.logout = 0
        self.u = User.objects.get(roomid=roomid)
        self.roomid = roomid
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
        self.u.energy = self.energy
        # 若已经到达目标风速
       # if self.cur_temp == self.tar_temp:

        self.u.save()

    def run(self):

        while self.logout != 1:
            time.sleep(0.5)
            during_time = time.time() - self.time
            if during_time > self.frequency:
                self.syntax()
                # 开机状态，且风速不为零
                if self.u.state == 1 and self.u.speed != 0:

                    temp = self.rate + (self.speed - 1) * self.rate * 0.2  # 每分钟温度变化度数
                    self.energy += self.energyRate * self.speed / 3
                    self.cost += self.energyRate * self.speed / 3
                    if self.tar_temp > self.cur_temp:

                        self.cur_temp = min(float(self.cur_temp) + temp,
                                            float(self.tar_temp))

                    elif self.tar_temp < self.cur_temp:

                        self.cur_temp = max(float(self.cur_temp) - temp,
                                            float(self.tar_temp))
                    elif round(self.tar_temp) == round(self.cur_temp):
                        self.cur_temp = round(self.cur_temp)
                        self.update()
                        self.u.state = 2
                        self.u.speed=0
                        self.u.save()
                        self.u.wait_time=20
                        m.setInstance(self.u)
                        daily_temp = dailyreport.objects.get(roomid=self.u.roomid)
                        daily_temp.dispatch_times += 1
                        daily_temp.save()
                        m.Dispatch()
                        self.time = time.time()
                        continue

                    print("房间：" + str(self.u.roomid) + " 风速为" + str(self.speed)
                          + " 当前温度为" + str(self.cur_temp)
                          + " 当前花费为" + str(self.cost)
                          + " 时间：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    # 当前状态为挂起或者关闭，风速为零，当前温度不等于外部温度,
                elif self.cur_temp != self.out_temp and self.u.speed == 0:
                    temp = self.shutDownRate
                    if self.out_temp > self.cur_temp:
                        self.cur_temp = min(float(self.cur_temp) + temp,
                                            float(self.out_temp))
                    if self.out_temp < self.cur_temp:
                        self.cur_temp = max(float(self.cur_temp) - temp,
                                            float(self.out_temp))
                    print("房间：" + str(self.u.roomid) + "无风速，当前温度为" + str(self.cur_temp)
                          + " 当前花费为" + str(self.cost)
                          + " 时间：" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

                self.time = time.time()
                self.update()

    # 将用户请求加入队列
    def push(self):
        pass

    # 退出
    def logout(self):
        self.logout = 1

    # 获取等待队列
    def getWaitQueue(self):
        pass

    # 处理用户请求
    def doJob(self):
        pass


executor = ThreadPoolExecutor(max_workers=16)
slaves = []


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
def getInfo(roomid):
    u_update = User.objects.get(roomid=roomid)
    if u_update.state == 0:
        state = "关闭"
    elif u_update.state == 1:
        state = "开启"
    else:
        state = "挂起"
    if g['mode'] == 0:
        mode = "制冷"
    else:
        mode = "制热"
    data = {
        'isError': 0,
        'cur_temp': u_update.cur_temp,
        'tar_temp': u_update.tar_temp,
        'speed': u_update.speed,
        'cost': u_update.cost,
        'state': state,
        'mode': mode,
    }
    return data


def slave(request, roomid):
    try:

        data = getInfo(roomid)
        return JsonResponse(data)
    except:
        return HttpResponse("gg", 404)


def index(request, roomid):
    return render(request, "customer.html", {'room_id': roomid})


# 登录注册客户信息
@csrf_exempt
def login(request):
    try:
        # try:
        #     DailyReport()
        #
        # except Exception:
        #     str = 'traceback.format_exc():\n%s' % traceback.format_exc()
        #     print(str)

        if request.method == 'POST':
            username = request.POST['room_id']
            u = User.objects.get(roomid=username)
            return JsonResponse({"content": "注册失败！"})

    except Exception:
        if request.method == 'POST':
            username = request.POST['room_id']

            u = User(roomid=username, cur_temp=g["default_temp"], tar_temp=g["default_temp"])
            u.save()



        r = dailyreport(roomid=username, time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        r.save()
        str2 = 'traceback.format_exc():\n%s' % traceback.format_exc()
        print(str2)
        slave = Slave()
        slave.init(username, g["default_temp"])
        executor.submit(slave.run)
        slaves.append(slave)
        return HttpResponseRedirect('/slave/' + username + '/index')  # 跳转到index界面


# 从控机开机
def turnOn(request, roomid):
    if m.status == 0:
        content = '主控机未打开，请联系酒店管理人员！'
        return JsonResponse({'isError': 1,
                             'content': content})

    u = User.objects.get(roomid=roomid)

    if u.state == 0:
        u.state = 2
        u.save()
        # t=Request.objects.filter(roomid='12')
        # during=time.time()-time.mktime(t[0].time.timetuple())

        m.setInstance(u)
        daily_temp = dailyreport.objects.get(roomid=u.roomid)
        daily_temp.dispatch_times += 1
        daily_temp.save()
        m.Dispatch()

        data = getInfo(roomid)

        return JsonResponse(data)

    return HttpResponse("开机失败")


# 从控机关机
def turnOff(request, roomid):
    try:
        u = User.objects.get(roomid=roomid)
        u.state = 0
        u.speed = 0
        u.save()

        daily_temp = dailyreport.objects.get(roomid=u.roomid)
        daily_temp.dispatch_times += 1
        daily_temp.save()

        m.setInstance(u)
        m.Dispatch()

        for x in slaves:
            if x.roomid == roomid:
                x.logout = 1

                break

        r = dailyreport.objects.get(roomid=roomid)
        r.use_times += 1
        r.save()
        return HttpResponse("关机成功")
    except Exception:

        str3 = 'traceback.format_exc():\n%s' % traceback.format_exc()
        return HttpResponse(str3, 404)


def tempControl(request, op, roomid):
    u = User.objects.get(roomid=roomid)

    if op == "high":
        try:
            u.tar_temp = u.tar_temp + 1
            if u.tar_temp > g['temp_highLimit']:
                content = '温度不能大于' + str(g['temp_highLimit'])
                return JsonResponse({'isError': 1,
                                     'content': content})
            u.save(update_fields=['tar_temp'])
            r = Request(roomid=roomid, temp=u.tar_temp, speed=-1, time=time.time(), cost=u.cost)
            r.save()
        except Exception:
            str1 = 'traceback.format_exc():\n%s' % traceback.format_exc()
            print(str1)
        # return HttpResponse("温度升高！")
    elif op == "low":
        u.tar_temp -= 1
        if u.tar_temp < g['temp_lowLimit']:
            content = '温度不能小于' + str(g['temp_lowLimit'])
            return JsonResponse({'isError': 1,
                                 'content': content})
        u.save(update_fields=['tar_temp'])
        r = Request(roomid=roomid, temp=u.tar_temp, speed=-1, time=time.time(), cost=u.cost)
        r.save()
        # return HttpResponse("温度降低")

        # return HttpResponse("wrong!!!please check url!", 404)
    data = getInfo(roomid)
    return JsonResponse(data)


def speedControl(request, op, roomid):
    u = User.objects.get(roomid=roomid)

    if op == "high":
        r = Request(roomid=roomid, temp=-1, speed=u.speed + 1, time=time.time(), cost=u.cost)
        r.save()
        u.speed += 1
        if u.speed > 3:
            content = '风速不能大于3！'
            return JsonResponse({'isError': 1,
                                 'content': content})
        if m.find_repeat(u, m.waitQueue):

            # u.speed += 1
            daily_temp = dailyreport.objects.get(roomid=u.roomid)
            daily_temp.dispatch_times += 1
            daily_temp.save()

            m.instance = u
            m.Dispatch()
        else:
            # u.speed += 1
            u.save()
        # return HttpResponse("风速升高")
    elif op == "low":
        r = Request(roomid=roomid, temp=-1, speed=u.speed - 1, time=time.time(), cost=u.cost)
        r.save()
        m.instance = u
        if m.find_repeat(u, m.waitQueue):
            daily_temp = dailyreport.objects.get(roomid=u.roomid)
            daily_temp.dispatch_times += 1
            daily_temp.save()
            m.Dispatch()
        else:
            u.speed -= 1
            if u.speed < 0:
                content = '风速不能小于0！'
                return JsonResponse({'isError': 1,
                                     'content': content})
            u.save()
        # return HttpResponse("风速降低")

        # return HttpResponse("wrong!!!please check url!", 404)
    data = getInfo(roomid)
    return JsonResponse(data)
