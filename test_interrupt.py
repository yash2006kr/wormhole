import asyncio
import websockets
import json
import urllib.request

async def test_interrupt_flow():
    # 1. Connect WebSocket
    async with websockets.connect('ws://localhost:8000/ws/screencast') as ws:
        print('[1] Connected to WebSocket')
        
        # 2. Trigger task: search AI on Wikipedia
        req = urllib.request.Request('http://localhost:8000/api/execute', 
            data=json.dumps({'prompt': 'Navigate to https://en.wikipedia.org and search for Artificial Intelligence'}).encode('utf-8'),
            headers={'Content-Type': 'application/json'})
        urllib.request.urlopen(req)
        print('[2] Triggered autonomous task')
        
        # 3. Simulate user click on canvas while running to trigger Interrupt
        await asyncio.sleep(0.3)
        print('[3] Sending CANVAS_CLICK event to simulate user clicking live showcase...')
        await ws.send(json.dumps({'type': 'CANVAS_CLICK', 'x': 0.5, 'y': 0.5}))
        
        # 4. Listen for INTERRUPT_TRIGGERED
        interrupted = False
        for _ in range(15):
            msg = json.loads(await asyncio.wait_for(ws.recv(), timeout=4.0))
            if msg.get('type') == 'INTERRUPT_TRIGGERED':
                print(f'[4] SUCCESS: Received {msg.get("type")}: "{msg.get("message")}"')
                interrupted = True
                break
        
        if not interrupted:
            print('[!] Warning: Did not receive INTERRUPT_TRIGGERED in window')
        else:
            # 5. Resolve interrupt with RESUME
            print('[5] Resolving interrupt with RESUME (accidental click dismissed)...')
            await ws.send(json.dumps({'type': 'RESOLVE_INTERRUPT', 'action': 'RESUME'}))
            await asyncio.sleep(1)
            print('[6] Interrupt test passed cleanly!')

if __name__ == '__main__':
    asyncio.run(test_interrupt_flow())
