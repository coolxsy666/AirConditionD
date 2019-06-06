from django.urls import path

from . import views
from .dao import slave,master
urlpatterns = [
    path('', views.index, name='index'),
    path(r'test/', views.testb, name='login'),
    # 客户
    path(r'login/<username>/', slave.login, name='login'),
    path(r'slave/<roomid>/', slave.slave),  # 从控机主页

    path(r'slave/temp/<op>/<roomid>/', slave.tempControl),  # 请求改变温度，op=high时增加一度，=low时减小
    path(r'slave/speed/<op>/<roomid>/', slave.speedControl),  # 同上，风速改变一档
    path(r'slave/turnon/<roomid>/', slave.turnOn),  # 打开从控机
    path(r'slave/turnoff/<roomid>/', slave.turnOff),

    # 经理
    path(r'queryreport/<roomid>/', views.queryReport),
    # 空调管理员
    path(r'master/', master.master, name='mast'),  # 主控机的主页
    path(r'startup/', master.startUP),  #
    path(r'setPara/', master.setPara),  # 设置启动参数
    path(r'checkstate/', master.checkState),  # 查看从控机状态
    path(r'closeup/', master.closeUp),  # 关闭
    path(r'editslave/<roomid>/', master.editSlave),  # 改变一个房间的状态
    # 前台
    path(r'printSpec/<roomid>/', views.printSpec),  # 打印详单
    path(r'printBill/<roomid>/', views.printBill),  # 打印账单
]
