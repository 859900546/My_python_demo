import asyncio
import threading
import time

import websockets

import audio_t


async def echo(websocket, path):
    print(websocket)
    try:
        async for message in websocket:
            if 'Get' in message:
                await websocket.send(next(audio_t.test()))
    except websockets.exceptions.ConnectionClosedError:
        pass
        # await websocket.send(message)


start_server = websockets.serve(echo, '0.0.0.0', 5001)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
