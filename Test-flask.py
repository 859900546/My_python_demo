import cv2
import pyautogui
from PIL import Image
from flask import Flask, render_template, Response, request, stream_with_context
import io
import dxshot

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('Test.html')


#  {{ url_for('video_feed') }}

@app.route('/pointer')
def pointer():
    x = int(float(request.args["xrate"]) * 1920)
    y = int(float(request.args["yrate"]) * 1080)
    # 执行点击操作
    pyautogui.click(x, y)
    return "success"


def gen():
    while True:
        img = dxshot.Cp.grab()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        # img.thumbnail((1920 // 2, 1080 // 2))
        # 图像压缩
        output_buffer = io.BytesIO()  # 建立二进制对象,在内存中读写
        # RGB格式压缩为JPEG格 式,quality: 保存图像的质量,1(最差)~100
        img.save(output_buffer, format='JPEG', quality=100)
        #        imgByteArr = img.getvalue()
        frame = output_buffer.getvalue()
        # print(type(frame))
        yield b'--frame\r\n Content-Type: image/jpeg\r\n\r\n' + frame


@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/audio_feed')
def audio_feed():
    return Response(audio_t.record(), mimetype="multipart/x-mixed-replace; boundary=myboundary")
    # return Response(stream_with_context(audio_t.record()))


# socketio = SocketIO(app)
#
#
# @socketio.on('connect')
# def handle_connect():
#     audio_generator = audio_t.record()
#     for audio_data in audio_generator:
#         socketio.send(audio_data)
#
# import asyncio
# import websockets
#
#
# async def echo(websocket, path):
#     try:
#         async for message in websocket:
#             if 'Get' in message:
#                 await websocket.send(next(audio_t.test()))
#     except websockets.exceptions.ConnectionClosedError:
#         pass
#         # await websocket.send(message)


#
def start():
    app.run(host='0.0.0.0', threaded=True)


if __name__ == '__main__':
    # socketio.run(app, host='0.0.0.0', port=5000)
    start()
    # threading.Thread(target=start).start()
    # start()
    # start_server = websockets.serve(echo, '0.0.0.0', 5001)
    # asyncio.get_event_loop().run_until_complete(start_server)
    # asyncio.get_event_loop().run_forever()
