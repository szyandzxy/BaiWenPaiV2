import aiofiles
import aiohttp
import asyncio
import chompjs
import re

from aiofiles.os import path, mkdir
from lxml import etree


# 下载图片，失败时打印错误但不中断整体任务
async def down_pic(session, pic_url, pic_path):
    try:
        async with session.get(pic_url) as resp:
            if resp.status != 200:
                print(f'[跳过] {pic_url} -> HTTP {resp.status}')
                return
            content = await resp.read()
        async with aiofiles.open(pic_path, 'wb') as f:
            await f.write(content)
        print(f'[OK] {pic_path}')
    except Exception as e:
        print(f'[错误] {pic_url} -> {e}')


# 从页面自动获取最新 JS 链接（兼容官网改版）
async def get_js_url(session):
    async with session.get('https://ssr.163.com/cardmaker/') as resp:
        html = await resp.text()
    # 取最后一个 ssr.res.netease.com 的 JS
    urls = re.findall(r'https://ssr\.res\.netease\.com[^\s\'"]+\.js', html)
    if not urls:
        raise RuntimeError('未找到卡牌数据 JS 链接')
    # index JS 通常是最后一个（不含 vendor）
    for u in reversed(urls):
        if 'vendor' not in u:
            return u
    return urls[-1]


# 从 JS 中提取卡牌数据列表
def extract_card_data(js_text):
    # 多种正则兼容不同版本
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
    raise RuntimeError('无法从 JS 中解析卡牌数据，请检查正则是否需要更新')


# 返回卡牌图片 url 和对应存储目录
async def get_card_info(session):
    card_info = []
    dir_dict = {}  # {card_role(int): card_name(str)}

    avatar_url = 'https://ssr.res.netease.com/pc/zt/20191112204330/data/shishen_avatar'
    card_url   = 'https://ssr.res.netease.com/pc/zt/20191112204330/data/card'

    js_url = await get_js_url(session)
    print(f'[JS] {js_url}')

    async with session.get(js_url) as resp:
        js_text = await resp.text()

    data = extract_card_data(js_text)
    print(f'[数据] 共 {len(data)} 条卡牌数据')

    for card in data:
        try:
            card_id   = int(card['id'])
            card_name = card['name'].replace('/', '-')
            card_role = int(card['role'])
            card_type = card['type']
        except (KeyError, ValueError, TypeError):
            continue

        if card_type == '式神':
            # 建立式神目录，记录 role→name 映射
            dir_path = f'./pic/{card_name}'
            if not await path.exists(dir_path):
                await mkdir(dir_path)
            dir_dict[card_role] = card_name

            # 式神头像（小图）
            card_info.append((
                f'{avatar_url}/{card_id}.png',
                f'./pic/{card_name}/avatar.png',
            ))
            # 式神立绘（与普通卡牌同路径，即 data/card/{id}.png）
            card_info.append((
                f'{card_url}/{card_id}.png',
                f'./pic/{card_name}/card.png',
            ))
        else:
            if card_role not in dir_dict:
                # 式神目录还未建立（数据顺序问题），跳过
                print(f'[警告] role={card_role} 目录未建立，跳过 {card_name}')
                continue
            card_info.append((
                f'{card_url}/{card_id}.png',
                f'./pic/{dir_dict[card_role]}/{card_name}.png',
            ))

    return card_info


async def main():
    # 并发数限制，避免对服务器造成压力
    sem = asyncio.Semaphore(20)

    async def down_with_sem(session, url, path_):
        async with sem:
            await down_pic(session, url, path_)

    async with aiohttp.ClientSession() as session:
        card_info = await get_card_info(session)
        print(f'[任务] 共 {len(card_info)} 张图片待下载')
        tasks = [down_with_sem(session, url, p) for url, p in card_info]
        await asyncio.gather(*tasks)
    print('[完成]')


if __name__ == '__main__':
    asyncio.run(main())
