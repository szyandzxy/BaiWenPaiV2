from os import mkdir, path
import requests
import demjson


def get_pic(pic_url, pic_path):
    response = s.get(pic_url)
    with open(pic_path, 'wb') as fp:
        fp.write(response.content)


def main():
    avatar_url = 'https://ssr.res.netease.com/pc/zt/20191112204330/data/shishen_avatar/'
    card_url = 'https://ssr.res.netease.com/pc/zt/20191112204330/data/card/'
    dir_dict = {}

    response = s.get('https://ssr.res.netease.com/pc/zt/20191112204330/js/index_d3b4b764.js')
    start_subscript = response.text.find('),d=[') + 4
    end_subscript = response.text.find(';function u(e')
    data = response.text[start_subscript:end_subscript]
    data_json = demjson.decode(data)  # 使用demjson库解析不正常json数据
    for v in data_json:
        card_id = str(v['id'])
        card_name = v['name']
        card_role = int(v['role'])  # 没有办法，role有int有string，得多处理一步
        card_type = v['type']

        # 为了炭治郎，我还得特意处理斜杠，平安京数值怪天天恶心我就算了，写个代码还恶心我。
        card_name = card_name.replace('/', '-')

        print('正在爬取: {}-{}'.format(card_id, card_name))

        # 如果是式神，创建文件夹存放此式神头像和所有卡牌
        if card_type == '式神':
            if not path.exists('./pic/' + card_name):
                mkdir('./pic/' + card_name)

            dir_dict[card_role] = card_name
            pic_path = './pic/{}/avatar.png'.format(dir_dict[card_role])
            get_pic(avatar_url + card_id + '.png', pic_path)

        pic_path = './pic/{}/{}.png'.format(dir_dict[card_role], card_name)
        get_pic(card_url + card_id + '.png', pic_path)


if __name__ == '__main__':
    s = requests.session()
    main()
