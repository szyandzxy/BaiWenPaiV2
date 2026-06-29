import asyncio
import aiohttp
import re

async def main():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ssr.163.com/cardmaker/') as resp:
            html = await resp.text()
        urls = re.findall(r'https://ssr\.res\.netease\.com[^\s"\']+\.js', html)
        for u in urls:
            print(u)
        print('---')
        for u in reversed(urls):
            if 'vendor' not in u:
                js_url = u
                break
        print(f'Fetching: {js_url}')
        async with session.get(js_url) as resp:
            js_text = await resp.text()
        print(f'JS length: {len(js_text)}')
        # 搜索 d= 数组
        for pat in [r'd=\[', r',d=\[', r'JSON\.parse', r'=\[']:
            matches = list(re.finditer(pat, js_text))
            print(f'  {pat}: {len(matches)} matches')
            if matches:
                for m in matches[:3]:
                    start = max(0, m.start()-50)
                    end = min(len(js_text), m.end()+200)
                    snippet = js_text[start:end]
                    print(f'    ...{snippet}...')
        # 找大数组
        arr_matches = list(re.finditer(r'\[{.*?}\]', js_text[:100000], re.DOTALL))
        print(f'Large array candidates: {len(arr_matches)}')
        for m in arr_matches[:5]:
            print(f'  pos={m.start()}, len={m.end()-m.start()}, preview={js_text[m.start():m.start()+300]}')

asyncio.run(main())
