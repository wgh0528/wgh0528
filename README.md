# 电商产品生图网站（OpenAI）

支持能力：
- 一次生成多张电商图片（白底图 / 卖点图 / 详情页）
- 可选比例（1:1、4:3、3:4、16:9、9:16）
- 历史记录（可查看、下载）
- 图片转视频脚本（当前为“图片理解 + 短视频脚本生成”流程，便于后续接入视频模型）

## 1. 安装

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. 配置

```bash
cp .env.example .env
# 编辑 .env，填入 OPENAI_API_KEY
export OPENAI_API_KEY=你的Key
```

## 3. 启动

```bash
python app.py
```

浏览器访问：`http://localhost:8000`

## 4. 说明

- 图片生成接口使用 `client.images.generate(...)`。
- 默认模型设置为 `gpt-image-1`（你提到的 images-2 在 SDK 中通常以该模型名接入）。
- “根据图片生成视频”功能当前返回可直接用于剪辑的短视频脚本文案；如果你有指定的视频模型（如 Sora API 可用账号），可在 `/api/generate-video` 中替换为真实视频生成并落盘下载。

## 5. 目录

```text
.
├── app.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── app.js
│   └── style.css
├── outputs/        # 生成图片输出
└── data/history.json
```
