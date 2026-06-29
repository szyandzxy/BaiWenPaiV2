import asyncio, aiohttp, re, chompjs

async def test():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://ssr.163.com/cardmaker/') as resp:
            html = await resp.text()
        urls = re.findall(r'https://ssr\.res\.netease\.com[^\s\'\"]+\.js', html)
        js_url = None
        for u in reversed(urls):
            if 'vendor' not in u:
                js_url = u
                break
        if not js_url:
            js_url = urls[-1]

        async with session.get(js_url) as resp:
            js_text = await resp.text()

        # 用正则提取所有卡牌数据
        pat = r'\{id:(\d+),name:"([^"]+)",role:"?(\d+)"?,type:"([^"]+)"'
        items = re.findall(pat, js_text)
        print(f'正则匹配到 {len(items)} 条')

        # 构建完整数据
        keys_seen = set()
        for m in items:
            keys_seen.update(['id','name','role','type'])
        print(f'基础字段: {keys_seen}')

        # 检查是否有 xiyoudu, stage, ll, sm, desc, keyword 等字段
        extra = re.findall(r'xiyoudu:"([^"]*)"', js_text)
        print(f'xiyoudu 字段出现 {len(extra)} 次')

        # 看看完整的数据块结构
        idx = js_text.find('{id:66001')
        start = js_text.rfind('{', 0, idx)
        end = js_text.find('}', idx)
        block = js_text[start:end+1]
        print(f'\n完整数据块样例:')
        print(block)

        # 统计式神数
        shikigami = [m for m in items if m[3] == '式神']
        print(f'\n式神: {len(shikigami)} 个')
        print(f'前5个: {shikigami[:5]}')

        # 检查 role 范围
        roles = set(int(m[2]) for m in items)
        print(f'role 数: {len(roles)}, 范围: {min(roles)}~{max(roles)}')

asyncio.run(test())
