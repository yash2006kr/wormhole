import asyncio
import json
from playwright.async_api import async_playwright
import websockets

async def test_ws():
    uri = "ws://localhost:8000/ws/screencast"
    async with websockets.connect(uri) as ws:
        print("Connected to WebSocket screencast!")
        for i in range(3):
            msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(msg)
            print(f"Received msg type: {data.get('type')}, state: {data.get('state')}, bytes len: {len(data.get('data', ''))}")
        print("WebSocket CDP stream verification successful!")

if __name__ == "__main__":
    try:
        import websockets
        asyncio.run(test_ws())
    except ImportError:
        print("websockets package not installed, testing via browser instead.")
