from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path(r'login/', views.slave, name='login'),
    path(r'slave/', views.slave),
    path(r'master/', views.master, name='mast'),
    path(r'slave/temp/<op>/<id>', views.test),
    path(r'slave/speed/<op>/<id>', views.slave),
    path(r'slave/turnon/<id>', views.slave),
    path(r'slave/turnoff/<id>', views.slave),

    # 经理
    path(r'queryreport/<id>', views.slave),
    # 空调管理员
    path(r'startup/', views.slave),
    path(r'setPara/', views.slave),
    path(r'checkstate/<id>', views.slave),
    path(r'closeup', views.slave),

]
