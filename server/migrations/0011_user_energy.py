# Generated by Django 2.0 on 2019-06-06 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0010_auto_20190605_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='energy',
            field=models.IntegerField(default=0),
        ),
    ]
