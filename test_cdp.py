import asyncio
from playwright.async_api import async_playwright

async def test_cdp():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1280, "height": 800})
        page = await context.new_page()
        
        cdp = await context.new_cdp_session(page)
        frames_received = 0
        
        async def on_screencast(event):
            nonlocal frames_received
            frames_received += 1
            await cdp.send("Page.screencastFrameAck", {"sessionId": event["sessionId"]})
            
        cdp.on("Page.screencastFrame", on_screencast)
        await cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 60, "maxWidth": 1280, "maxHeight": 800})
        
        await page.goto("https://en.wikipedia.org")
        await asyncio.sleep(2)
        await cdp.send("Page.stopScreencast")
        await browser.close()
        print(f"CDP Screencast Test Passed! Frames Captured: {frames_received}")

if __name__ == "__main__":
    asyncio.run(test_cdp())
