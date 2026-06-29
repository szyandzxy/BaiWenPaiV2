import asyncio
import aiohttp
import re
import json

async def main():
    async with aiohttp.ClientSession() as session:
        # 获取页面
        async with session.get('https://ssr.163.com/cardmaker/') as resp:
            html = await resp.text()
        urls = re.findall(r'https://ssr\.res\.netease\.com[^\s"\']+\.js', html)
        for u in reversed(urls):
            if 'vendor' not in u:
                js_url = u
                break
        
        # 获取 index JS
        async with session.get(js_url) as resp:
            js_text = await resp.text()
        
        # 找大型数组 - 卡牌数据通常是一个大数组
        # 搜索 role/name/id/type 同时出现的地方
        matches = list(re.finditer(r'role["\':]\s*(\d+)[^}]*?name["\':]\s*["\']([^"\']+)[^}]*?type["\':]\s*["\']([^"\']+)', js_text))
        print(f'找到 {len(matches)} 个卡牌数据片段')
        
        # 收集所有式神
        shishen = {}
        cards = {}
        for m in matches:
            role = int(m.group(1))
            name = m.group(2)
            ctype = m.group(3)
            if ctype == '式神':
                shishen[role] = name
            else:
                if role not in cards:
                    cards[role] = []
                cards[role].append(name)
        
        print(f'\n=== 共 {len(shishen)} 个式神 ===\n')
        for role_id in sorted(shishen.keys()):
            name = shishen[role_id]
            card_list = cards.get(role_id, [])
            print(f'  [{role_id:3d}] {name} ({len(card_list)} 张卡牌)')

asyncio.run(main())
