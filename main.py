import aiofiles
import aiohttp
import asyncio
import chompjs
import re

from aiofiles.os import path, mkdir
from lxml import etree


# 下载图片
async def down_pic(session, pic_url, pic_path):
    print(pic_url, pic_path)
    async with session.get(pic_url) as resp:
        content = await resp.read()
    async with aiofiles.open(pic_path, 'wb') as f:
        await f.write(content)


# 返回卡牌图片 url 和对应存储目录
async def get_card_info(session):
    card_info = []  # 将会按照 [(pic1_url, pic1_path), (pic2_url, pic2_path) ...] 存储
    dir_dict = {}  # 式神 role 和 名字对应字典，{card_role: card_name}，为方便式神所属牌放置对应目录

    avatar_url = 'https://ssr.res.netease.com/pc/zt/20191112204330/data/shishen_avatar/'
    card_url = 'https://ssr.res.netease.com/pc/zt/20191112204330/data/card/'

    # 获取 js 链接
    async with session.get('https://ssr.163.com/cardmaker/') as resp:
        html = await resp.text()
    js_url = etree.HTML(html).xpath('/html/body/script[5]/@src')[0]

    # 取出 js 中的卡片数据
    async with session.get(js_url) as resp:
        html = await resp.text()
    data_str = re.findall(r"\(n\),d=(.*?);function u", html)[0]

    data = chompjs.parse_js_object(data_str)  # 使用 chompjs 解析 javascript objects

    for card in data:
        card_id = int(card['id'])  # 有的是 float 类型，需要转成 int 才能获取到图片
        card_name = card['name']
        card_role = int(card['role'])  # 有的是 string，统一成 int
        card_type = card['type']
        # print(card_id, card_name, card_role, card_type)

        card_name = card_name.replace('/', '-')  # 处理名字中的斜杠，避免写入文件出错

        # 按照卡片类型获取图片 url 和对应保存路径
        # 如果是卡片类型是[式神]，创建文件夹
        if card_type == '式神':
            if not await path.exists(f'./pic/{card_name}'):
                await mkdir(f'./pic/{card_name}')
            dir_dict[card_role] = card_name
            pic_url = f'{avatar_url}/{card_id}.png'
            pic_path = f'./pic/{dir_dict[card_role]}/avatar.png'

        # 如果卡片类型是（[战斗]、[形态]、[法术]...）
        else:
            pic_url = f'{card_url}/{card_id}.png'
            pic_path = f'./pic/{dir_dict[card_role]}/{card_name}.png'

        card_info.append((pic_url, pic_path))

    return card_info


async def main():
    tasks = []
    async with aiohttp.ClientSession() as session:
        card_info = await get_card_info(session)
        for (pic_url, pic_path) in card_info:
            tasks.append(down_pic(session, pic_url, pic_path))
        await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(main())
