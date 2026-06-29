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
        
        # 找 API 调用相关
        for keyword in ['getCardList', 'getCard', 'cardList', 'allCard', 'shishen', 'role', 'api']:
            idx = js_text.find(keyword)
            count = 0
            while idx != -1 and count < 3:
                start = max(0, idx - 100)
                end = min(len(js_text), idx + 400)
                snippet = js_text[start:end]
                # 只打印包含 url 或 api 的片段
                if 'url' in snippet.lower() or 'api' in snippet.lower() or 'http' in snippet:
                    print(f'--- {keyword} at {idx} ---')
                    print(snippet)
                    print()
                idx = js_text.find(keyword, idx + 1)
                count += 1

asyncio.run(main())
