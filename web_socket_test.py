import asyncio
import websockets


async def connect():
    async with websockets.connect('ws://127.0.0.1:5001') as websocket:
        await websocket.send('Hello, WebSocket!')
        response = await websocket.recv()
        print(response)


asyncio.get_event_loop().run_until_complete(connect())
