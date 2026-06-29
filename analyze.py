import asyncio
import aiohttp
import re
import chompjs

async def get_js_url(session):
    async with session.get('https://ssr.163.com/cardmaker/') as resp:
        html = await resp.text()
    urls = re.findall(r"https://ssr\.res\.netease\.com[^\s\"']+\.js", html)
    if not urls:
        raise RuntimeError('未找到卡牌数据 JS 链接')
    for u in reversed(urls):
        if 'vendor' not in u:
            return u
    return urls[-1]

def extract_card_data(js_text):
    patterns = [
        r'\(n\),d=(.*?);function u',
        r'\bn\b,d=(\[.*?\]),\w=',
        r',d=(\[{.*?}\]),',
    ]
    for pat in patterns:
        m = re.search(pat, js_text, re.DOTALL)
        if m:
            try:
                data = chompjs.parse_js_object(m.group(1))
                if isinstance(data, list) and len(data) > 10:
                    return data
            except Exception:
                continue
    raise RuntimeError('无法从 JS 中解析卡牌数据')

async def main():
    async with aiohttp.ClientSession() as session:
        js_url = await get_js_url(session)
        print(f'JS URL: {js_url}')
        async with session.get(js_url) as resp:
            js_text = await resp.text()
        data = extract_card_data(js_text)
        print(f'总卡牌数据条数: {len(data)}')
        shishen = {}
        cards = {}
        for card in data:
            try:
                card_id = int(card['id'])
                card_name = card['name']
                card_role = int(card['role'])
                card_type = card['type']
            except (KeyError, ValueError, TypeError):
                continue
            if card_type == '式神':
                shishen[card_role] = card_name
            else:
                if card_role not in cards:
                    cards[card_role] = []
                cards[card_role].append(card_name)
        print(f'\n=== 共 {len(shishen)} 个式神 ===\n')
        for role_id in sorted(shishen.keys()):
            name = shishen[role_id]
            card_list = cards.get(role_id, [])
            print(f'  [{role_id:3d}] {name} ({len(card_list)} 张卡牌)')
        total_cards = sum(len(v) for v in cards.values())
        print(f'\n总卡牌数（不含式神本体）: {total_cards}')

asyncio.run(main())
