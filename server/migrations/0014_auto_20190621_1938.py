# Generated by Django 2.0 on 2019-06-21 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0013_auto_20190621_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyreport',
            name='time',
            field=models.DateTimeField(),
        ),
    ]
