import asyncio
import aiohttp
import re

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ssr.163.com/cardmaker/') as resp:
            html = await resp.text()
        urls = re.findall(r'https://ssr\.res\.netease\.com[^\s"\']+\.js', html)
        for u in reversed(urls):
            if 'vendor' not in u:
                js_url = u
                break
        
        async with session.get(js_url) as resp:
            js_text = await resp.text()
        
        # 找 role 出现的位置
        for keyword in ['role', 'shishen', 'avatar', 'card_id', 'shikigami']:
            idx = js_text.find(keyword)
            count = 0
            while idx != -1 and count < 5:
                start = max(0, idx - 50)
                end = min(len(js_text), idx + 150)
                snippet = js_text[start:end]
                print(f'[{keyword} at {idx}]: ...{snippet}...')
                print()
                idx = js_text.find(keyword, idx + 1)
                count += 1

asyncio.run(main())
