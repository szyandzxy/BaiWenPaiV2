import asyncio
import aiohttp
import re
import json

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
        
        # 从 role 开始找数组
        # 数据格式: [{id:66700,name:"待宵姑获鸟",role:"667",type:"式神",...},...]
        # 找到第一个 {id: 开头的完整数组
        idx = js_text.find('{id:')
        # 往前找 [ 开头
        arr_start = js_text.rfind('[', idx-1000, idx)
        print(f'Array starts at {arr_start}')
        
        # 找匹配的 ]
        depth = 0
        arr_end = arr_start
        for i in range(arr_start, min(arr_start + 500000, len(js_text))):
            c = js_text[i]
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    arr_end = i + 1
                    break
        
        arr_text = js_text[arr_start:arr_end]
        print(f'Array text length: {len(arr_text)}')
        
        # 转成合法 JSON
        # 把 JS 对象转成 JSON: 加引号
        arr_json = arr_text
        # 替换 key: 为 "key":
        arr_json = re.sub(r'(\w+):', r'"\1":', arr_json)
        # 替换单引号为双引号
        arr_json = arr_json.replace("'", '"')
        
        data = json.loads(arr_json)
        print(f'总数据条数: {len(data)}')
        
        shishen = {}
        cards = {}
        for card in data:
            try:
                card_id = int(card['id'])
                card_name = card['name']
                card_role = card['role']
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
        for role_id in sorted(shishen.keys(), key=lambda x: int(x)):
            name = shishen[role_id]
            card_list = cards.get(role_id, [])
            print(f'  [{role_id:>4s}] {name} ({len(card_list)} 张卡牌)')
        
        total_cards = sum(len(v) for v in cards.values())
        print(f'\n总卡牌数（不含式神本体）: {total_cards}')

asyncio.run(main())
