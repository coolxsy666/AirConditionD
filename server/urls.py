from django.urls import path

from . import views
from .dao import slave
urlpatterns = [
    path('', views.index, name='index'),
    path(r'test/', views.testb, name='login'),
    # 客户
    path(r'login/<username>/', views.login, name='login'),
    path(r'slave/<roomid>/', views.slave),  # 从控机主页

    path(r'slave/temp/<op>/<roomid>/', views.tempControl),  # 请求改变温度，op=high时增加一度，=low时减小
    path(r'slave/speed/<op>/<roomid>/', views.speedControl),  # 同上，风速改变一档
    path(r'slave/turnon/<roomid>/', slave.turnOn),  # 打开从控机
    path(r'slave/turnoff/<roomid>/', views.turnOff),

    # 经理
    path(r'queryreport/<roomid>/', views.queryReport),
    # 空调管理员
    path(r'master/', views.master, name='mast'),  # 主控机的主页
    path(r'startup/', views.startUP),  #
    path(r'setPara/', views.setPara),  # 设置启动参数
    path(r'checkstate/', views.checkState),  # 查看从控机状态
    path(r'closeup/', views.closeUp),  # 关闭
    path(r'editslave/<roomid>/', views.editSlave),  # 改变一个房间的状态
    # 前台
    path(r'printSpec/<roomid>/', views.printSpec),  # 打印详单
    path(r'printBill/<roomid>/', views.printBill),  # 打印账单
]
