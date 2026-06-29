import asyncio
import aiohttp
import chompjs
import re

async def get_js_url(session):
    async with session.get('https://ssr.163.com/cardmaker/') as resp:
        html = await resp.text()
    urls = re.findall(r"https://ssr\.res\.netease\.com[^\s\"']+\.js", html)
    for u in reversed(urls):
        if 'vendor' not in u:
            return u
    return urls[-1]

def extract_card_data(js_text):
    idx = js_text.find('[{id:')
    if idx == -1:
        raise RuntimeError('not found')
    depth = 0
    for i in range(idx, len(js_text)):
        c = js_text[i]
        if c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                arr_text = js_text[idx:i+1]
                return chompjs.parse_js_object(arr_text)
    raise RuntimeError('no end')

async def main():
    async with aiohttp.ClientSession() as session:
        js_url = await get_js_url(session)
        print(f'JS: {js_url}')
        async with session.get(js_url) as resp:
            js_text = await resp.text()
        data = extract_card_data(js_text)
        shishen = sum(1 for c in data if c.get('type') == '式神')
        print(f'总数据: {len(data)}, 式神: {shishen}')

asyncio.run(main())
