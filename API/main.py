import asyncio
from datetime import datetime, timedelta

from fastapi import FastAPI, WebSocket
import uvicorn

from data.database.controller import TickDataController
from data.feeder.feeder import Feeder

from data.database.schema import Base, engine
app = FastAPI()
@app.websocket("/ws/{pair}/{timeframe}")
async def send_data(websocket: WebSocket, pair: str, timeframe: int):
    await websocket.accept()

    # Initialize the TickDataController and Feeder
    Base.metadata.create_all(bind=engine)
    controller = TickDataController()
    last_date = controller.get_last_date(pair)
    if last_date is None:
        feeder = Feeder(pair)
    else:
        feeder = Feeder(pair, last_date)

    # Send initial data to the client
    await websocket.send_json(controller.get_from(timeframe, (datetime.now() - timedelta(minutes=timeframe*20)).timestamp(), pair).to_json())

    # Set up caching
    cache_size = 32
    cache = []

    # Continuously send new ticks data
    while True:
        new_ticks = feeder.get_ticks()
        if new_ticks:
            cache += new_ticks
            for tick in new_ticks:
                await asyncio.sleep(0.05)
                await websocket.send_json(tick)
        if len(cache) >= cache_size:
            # Add cached ticks to the database
            controller.add_ticks(cache, pair)
            cache = []



if __name__=='__main__':
    uvicorn.run(app, host="127.0.0.1", port=4444)



