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
        
        # 找 data_list 相关 - 这是卡牌数据加载的地方
        idx = js_text.find('data_list')
        while idx != -1:
            start = max(0, idx - 300)
            end = min(len(js_text), idx + 800)
            print(f'--- data_list at {idx} ---')
            print(js_text[start:end])
            print()
            idx = js_text.find('data_list', idx + 1)
            if idx > 300000:
                break

asyncio.run(main())
