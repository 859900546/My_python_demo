import queue
import socket
import sys
import threading
import time
import pyaudio
import webbrowser
from loguru import logger

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 307366)
server_address = ('127.0.0.1', 6618)
udp_socket.settimeout(0.1)

# udp_socket.bind(server_address)

p = pyaudio.PyAudio()
index = 1
format_ = pyaudio.paInt16
channels = 2
rate = 44100
chunk = 1024
dev_index = int(p.get_default_output_device_info()['index'])

out_stream = p.open(output_device_index=dev_index, format=format_, channels=channels, rate=rate, output=True,
                    frames_per_buffer=chunk)

buffer = queue.Queue()  # 缓冲区
buffer_max_size = 10
FPS = 240


def buffer_check():
    while True:
        if buffer.qsize() >= 2:
            out_stream.write(buffer.get()[0])
        else:
            time.sleep(10 / FPS)


def record():
    while True:
        try:
            data = udp_socket.recvfrom(4096)
        except socket.timeout:
            time.sleep(0.01)
            continue
        yield data


# loguru.logger.remove()
if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> - <level>{"
                                  "message}</level>",
               colorize=True)
    threading.Thread(target=buffer_check).start()  # 缓冲区线程
    url = 'http://10.22.218.145:5000/'
    logger.info(f'屏幕共享网址:{url}')
    webbrowser.open(url)
    while True:
        udp_socket.sendto(b'', server_address)
        logger.info(f'地址：{next(record())[1]}')
        break
    logger.info(f'开始传输音频，FPS:{FPS}')
    for i in record():
        buffer.put(i)
        # if buffer.qsize() >= 18:
        #     time.sleep(0.01)
