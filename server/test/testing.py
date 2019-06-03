import threading
from time import sleep
from server.models import User





def testa():
    sleep(1)
    print("a")


def testb():
    sleep(1)
    print("b")

    u = User.objects.get(roomid="qwe")
    g["test"] = "test123"
    g["User"] = u
    # 先隔出一秒打印出a，再过一秒打出b
    ta = threading.Thread(target=testa)
    tb = threading.Thread(target=testb)
    for t in [ta, tb]:
        t.start()
    for t in [ta, tb]:
        t.join()
    print("DONE")
    print(g)

# 输出是ab或者ba（紧贴着的）然后空一行再来DONE的结果。
