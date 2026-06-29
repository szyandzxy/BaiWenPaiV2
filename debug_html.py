import asyncio
import aiohttp
import re

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ssr.163.com/cardmaker/') as resp:
            html = await resp.text()
        
        # 看看页面里有没有直接的数据
        print(f'HTML length: {len(html)}')
        
        # 找 script 标签
        scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', html)
        print(f'Script tags: {len(scripts)}')
        for i, s in enumerate(scripts):
            if len(s) > 1000:
                print(f'\nScript {i}: {len(s)} chars')
                print(s[:500])
                print('...')
                print(s[-500:])
        
        # 找 JSON 数据
        json_matches = re.findall(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html, re.DOTALL)
        print(f'\n__INITIAL_STATE__: {len(json_matches)}')
        if json_matches:
            print(json_matches[0][:1000])

asyncio.run(main())
