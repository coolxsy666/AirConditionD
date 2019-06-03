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

    def init(self):
        self.status = 0
        self.default_temp = g["default_temp"]#初始外界温度以及空调初始设置温度
        self.temp_highLimit = g["temp_highLimit"]
        self.temp_lowLimit = g["temp_lowLimit"]
        self.feeRate_H = g["feeRate_H"]
        self.feeRate_M = g["feeRate_M"]
        self.feeRate_L = g["feeRate_L"]
        self.handleNum = g["handleNum"]
        self.cur_feeRate = self.feeRate_M  # 设置初始费率为中等
        #删除所有请求
        Request.delete()
        #重置所有房间初始信息
        for item in User.objects.all():
            if self.mode==0:
                item.speed=0
                item.tar_temp=22
                item.save()
            elif self.mode==1:
                item.speed=0;
                item.tar_temp=28
                item.save()





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
