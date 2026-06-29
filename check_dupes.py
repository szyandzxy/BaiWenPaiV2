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
    depth = 0
    for i in range(idx, len(js_text)):
        c = js_text[i]
        if c == '[': depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                return chompjs.parse_js_object(js_text[idx:i+1])
    raise RuntimeError('no end')

async def main():
    async with aiohttp.ClientSession() as session:
        js_url = await get_js_url(session)
        async with session.get(js_url) as resp:
            js_text = await resp.text()
        data = extract_card_data(js_text)
    
    # 找同名卡牌
    from collections import defaultdict
    names = defaultdict(list)
    for card in data:
        try:
            name = card['name']
            cid = card['id']
            ctype = card['type']
            if ctype != '式神':
                names[name].append((cid, card.get('role', '')))
        except:
            continue
    
    dupes = {k: v for k, v in names.items() if len(v) > 1}
    print(f"同名卡牌组数: {len(dupes)}")
    for name, items in sorted(dupes.items()):
        print(f"  {name}: {[f'id={i[0]}, role={i[1]}' for i in items]}")

asyncio.run(main())
