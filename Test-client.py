import dxshot
from io import BytesIO

from PIL import Image
from network import client_peocess

tcp = client_peocess.TCP(ip='192.168.3.81', port=6618)


def example():
    while True:
        img = dxshot.Cp.grab()
        img = Image.fromarray(img)
        # img.thumbnail((1920 // 2, 1080 // 2))
        # 图像压缩
        output_buffer = BytesIO()  # 建立二进制对象,在内存中读写
        # RGB格式压缩为JPEG格 式,quality: 保存图像的质量,1(最差)~100
        img.save(output_buffer, format='JPEG', quality=100)
        yield output_buffer


def test(img):
    tcp.send_img(img)


tcp.connect_server()
for i in example():
    tcp.send_img(i)
