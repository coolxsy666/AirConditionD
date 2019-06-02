# Generated by Django 2.0 on 2019-06-02 07:34

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='dailyreport',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('roomid', models.CharField(max_length=45)),
                ('time', models.DateField(auto_now=True)),
                ('use_times', models.IntegerField(default=0)),
                ('fre_temp', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('fre_speed', models.IntegerField(default=0)),
                ('dispatch_times', models.IntegerField(default=0)),
                ('details_times', models.IntegerField(default=0)),
                ('sumcost', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('roomid', models.CharField(max_length=45)),
                ('temp', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('speed', models.IntegerField(default=0)),
                ('time', models.DateField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('roomid', models.CharField(max_length=45)),
                ('tar_temp', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('cur_temp', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
                ('speed', models.IntegerField(default=0)),
                ('cost', models.DecimalField(decimal_places=2, default=0, max_digits=3)),
            ],
        ),
    ]
