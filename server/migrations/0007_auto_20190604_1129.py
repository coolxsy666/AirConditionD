# Generated by Django 2.0 on 2019-06-04 03:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0006_user_is_suspended'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='time',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
