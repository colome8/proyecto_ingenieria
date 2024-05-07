import time
import asyncio
import websockets
import uuid
import json


async def connect():
    async with websockets.connect('ws://127.0.0.1:4444/ws/EURUSD/5',timeout=60) as connection:
        while True:
            await asyncio.sleep(0.05)
            msg = await connection.recv()
            print(msg)

if __name__=='__main__':
    asyncio.run(connect())