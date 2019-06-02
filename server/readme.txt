1、raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__) 　　　
django.core.exceptions.ImproperlyConfigured: mysqlclient 1.3.13 or newer is required; you have 0.9.3. 　　
解决办法：C:\Python37\Lib\site-packages\django\db\backends\mysql（python安装目录）打开base.py，注释掉以下内容： 　　　　　　　
if version < (1, 3, 13): 　　　　　　　　　　
raise ImproperlyConfigured('mysqlclient 1.3.13 or newer is required; you have %s.' % Database.__version__) 　　
2、File "C:\Python37\lib\site-packages\django\db\backends\mysql\operations.py", line 146, in last_executed_query 　　
query = query.decode(errors='replace') 　　AttributeError: 'str' object has no attribute 'decode' 　　
解决办法：打开此文件把146行的decode修改为encode