import asyncio
import aiohttp
import re

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ssr.163.com/cardmaker/') as resp:
            html = await resp.text()
        
        print(html)

asyncio.run(main())
