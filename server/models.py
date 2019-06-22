# Create your models here.
from datetime import timezone

# coding=utf-8
from django.db import models


class dailyreport(models.Model):
    roomid = models.CharField(max_length=45)
    time = models.DateTimeField(auto_now=False)
    use_times = models.IntegerField(default=0)
    fre_temp = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    fre_speed = models.IntegerField(default=0)
    dispatch_times = models.IntegerField(default=0)
    details_times = models.IntegerField(default=0)
    change_temp_times=models.IntegerField(default=0)
    change_speed_times=models.IntegerField(default=0)
    sumcost = models.DecimalField(max_digits=7, decimal_places=2, default=0)


class User(models.Model):
    roomid = models.CharField(max_length=45)
    state = models.IntegerField(default=0)
    tar_temp = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    cur_temp = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    speed = models.IntegerField(default=0)
    energy =models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    serve_time = models.IntegerField(default=0)
    wait_time = models.IntegerField(default=0)


class Request(models.Model):
    roomid = models.CharField(max_length=45)
    temp = models.DecimalField(max_digits=4, decimal_places=2, default=0)
    speed = models.IntegerField(default=0)
    time = models.DateTimeField(auto_now=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2, default=0)
