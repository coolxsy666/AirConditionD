import time
from server.models import *
#从控机
class Slave:
    u=None
    status = 0  # 运行状态 为1则处于运行状态
    is_suspended=0 #是否被挂起，为1则被挂起

    cur_temp=0
    tar_temp=0
    out_temp=0
    speed=0
    cost=0#当前总计花费

    startTime=0#启动时间

    #从机初始化
    def init(self,roomid,out_temp):
        self.u=User.objects.get(roomid=roomid)


        self.out_temp=self.cur_temp=out_temp
        self.tar_temp=self.u.tar_temp
        self.update()
        self.startTime = time.time()

#若目标温度已到达，则风速降为0
    def update(self):
        self.u.cur_temp = round(self.cur_temp)
        if self.cur_temp == self.tar_temp: self.u.speed = 0
        self.u.save()


        pass
    def update(self):
        pass

    def run(self):
        pass

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
