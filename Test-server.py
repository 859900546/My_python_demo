import queue
import threading
import time
import cv2
from network import server_process
import matplotlib.image as image

udp = server_process.UDP(port=6618)


# tcp.init()


def get_img():
    while True:
        imgx = udp.recv_img()
        yield imgx


def example():
    while True:
        imgx = next(get_img())
        # img = BytesIO(img)
        if imgx is not None:
            try:
                imgx = image.imread(imgx, format='jpeg')
            except:
                continue
        yield imgx


buffer = queue.Queue(maxsize=600)

s = 0
x = 0


#
def show():
    global s, x
    for i in example():
        buffer.put(i)
        if buffer.qsize() >= 200:
            time.sleep(0.02)


threading.Thread(target=show).start()
#
img = None
# while True:
#     if buffer.qsize() >= 5:
#         # time.sleep(0.05)
while True:
    if buffer.qsize() >= 2:
        img = buffer.get()
    else:
        time.sleep(0.002)
        # continue
    if img is not None:
        cv2.imshow("wi", img)
        cv2.waitKey(1)
        x = time.time()
    # time.sleep(0.002)
    # if buffer.qsize() < 2:
    #     break
    else:
        time.sleep(0.008)

    # threading.Thread(target=show,args=(i,)).start()
    # plt.pause(0.05)
    # plt.ioff()  # 关闭画图的窗口
