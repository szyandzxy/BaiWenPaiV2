# BaiWenPaiV2

从 [官网](https://ssr.163.com/cardmaker/) 爬取百闻牌全部卡面图片及式神立绘。

## 目录结构

```
pic/
  妖刀姬/
    avatar.png   # 式神头像（小图）
    card.png     # 式神立绘（大图）
    一闪.png
    见切.png
    ...
  影鳄/
    avatar.png
    card.png
    出蛰.png
    ...
```

## 使用

```bash
pip install -r requirements.txt
python main.py
```

## 更新说明

- 新增式神立绘下载（`card.png`），原项目仅下载头像
- 修复官网 JS 结构变更导致的解析失败问题
- 下载失败自动跳过并打印错误，不中断整体任务
- 并发限制 20，避免对服务器造成压力

## 旧项目

[BaiWenPai](https://github.com/YEOLLL/BaiWenPai)（已停止更新）
[BaiWenPaiV2 原版](https://github.com/szyandzxy/BaiWenPaiV2/tree/v1)
