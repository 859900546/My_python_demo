import av
from io import BytesIO

# 创建一个 BytesIO 对象
import dxshot

output_bytes = BytesIO()

# 创建一个输出容器
container = av.open("output_bytes.mp4", 'wb', format='mp4')

# 添加视频流
stream = container.add_stream('h264', rate=30)  # 使用 H.264 编码，帧率为 30
stream.width = 1920  # 视频宽度
stream.height = 1080  # 视频高度

n = 30
while n > 0:
    n -= 1
    img = dxshot.Cp.grab()
    img = av.VideoFrame.from_ndarray(img, format='rgb24')
    # img = img.reformat('yuv420p')
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    packet = stream.encode(img)
    container.mux(packet)
container.close()

# 读取 BytesIO 对象中的数据
# output_bytes.seek(0)
# video_data = output_bytes.read()
print(output_bytes.getvalue())
