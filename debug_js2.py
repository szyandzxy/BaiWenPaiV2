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
        print(f'Fetching: {js_url}')
        async with session.get(js_url) as resp:
            js_text = await resp.text()
        
        # 找 card_info 相关代码
        idx = js_text.find('card_info')
        while idx != -1:
            start = max(0, idx - 200)
            end = min(len(js_text), idx + 500)
            print(f'--- card_info at {idx} ---')
            print(js_text[start:end])
            print()
            idx = js_text.find('card_info', idx + 1)
            if idx > 200000:
                break

asyncio.run(main())
