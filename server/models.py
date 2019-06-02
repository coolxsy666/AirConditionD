# Create your models here.
from datetime import timezone

from django.db.models import IntegerField

# coding=utf-8
from django.db import models


class dailyreport(models.Model):
    id = models.IntegerField(primary_key=True)
    roomid = models.CharField(max_length=45)
    time = models.DateField(auto_now=True)
    use_times = models.IntegerField(default=0)
    fre_temp = models.DecimalField(max_digits=4,decimal_places=2,default=0)
    fre_speed = models.IntegerField(default=0)
    dispatch_times = models.IntegerField(default=0)
    details_times = models.IntegerField(default=0)
    sumcost = models.DecimalField(max_digits=4,decimal_places=2,default=0)


class User(models.Model):
    id = models.IntegerField(primary_key=True)
    roomid = models.CharField(max_length=45)
    tar_temp = models.DecimalField(max_digits=4,decimal_places=2,default=0)
    cur_temp = models.DecimalField(max_digits=4,decimal_places=2,default=0)
    speed = models.IntegerField(default=0)
    cost = models.DecimalField(max_digits=7,decimal_places=2,default=0)


class Request(models.Model):
    id = models.IntegerField(primary_key=True)
    roomid = models.CharField(max_length=45)
    temp = models.DecimalField(max_digits=4,decimal_places=2,default=0)
    speed = models.IntegerField(default=0)
    time = models.DateField(auto_now=True)
