import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from flask import Flask, jsonify, render_template, request, send_from_directory
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"
HISTORY_FILE = DATA_DIR / "history.json"

DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
if not HISTORY_FILE.exists():
    HISTORY_FILE.write_text("[]", encoding="utf-8")

app = Flask(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

IMAGE_STYLES = {
    "white_bg": "电商白底图风格，主体清晰，背景纯白，商业摄影质感",
    "selling_points": "电商卖点图风格，强调核心卖点，信息层级清晰，视觉冲击力强",
    "detail_page": "电商详情页风格，兼顾场景展示与细节特写，适合商品详情展示",
}

ASPECT_SIZES = {
    "1:1": "1024x1024",
    "4:3": "1536x1152",
    "3:4": "1152x1536",
    "16:9": "1792x1024",
    "9:16": "1024x1792",
}


def load_history():
    return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))


def save_history(records):
    HISTORY_FILE.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")


@app.route("/")
def index():
    return render_template("index.html", ratios=list(ASPECT_SIZES.keys()))


@app.route("/api/generate-images", methods=["POST"])
def generate_images():
    data = request.json or {}
    prompt = (data.get("prompt") or "").strip()
    style = data.get("style", "white_bg")
    ratio = data.get("ratio", "1:1")
    n = int(data.get("count", 1))

    if not prompt:
        return jsonify({"error": "请输入商品描述"}), 400
    if style not in IMAGE_STYLES:
        return jsonify({"error": "无效风格"}), 400
    if ratio not in ASPECT_SIZES:
        return jsonify({"error": "无效比例"}), 400
    if n < 1 or n > 10:
        return jsonify({"error": "一次最多生成10张"}), 400

    full_prompt = f"{IMAGE_STYLES[style]}。商品描述：{prompt}"
    size = ASPECT_SIZES[ratio]

    response = client.images.generate(
        model="gpt-image-1",
        prompt=full_prompt,
        size=size,
        n=n,
    )

    created_at = datetime.utcnow().isoformat()
    batch_id = str(uuid.uuid4())
    paths: List[str] = []

    import base64
    for i, item in enumerate(response.data):
        image_bytes = base64.b64decode(item.b64_json)
        filename = f"{batch_id}_{i+1}.png"
        file_path = OUTPUT_DIR / filename
        file_path.write_bytes(image_bytes)
        paths.append(f"/outputs/{filename}")

    records = load_history()
    records.insert(0, {
        "id": batch_id,
        "type": "images",
        "prompt": prompt,
        "style": style,
        "ratio": ratio,
        "count": n,
        "items": paths,
        "created_at": created_at,
    })
    save_history(records)

    return jsonify({"id": batch_id, "items": paths})


@app.route("/api/generate-video", methods=["POST"])
def generate_video():
    data = request.json or {}
    image_url = data.get("image_url")
    prompt = (data.get("prompt") or "")

    if not image_url:
        return jsonify({"error": "请提供图片地址"}), 400

    # 使用 OpenAI 视频生成接口（根据当前 SDK 版本可能命名不同）
    # 这里采用 responses API 的通用方式，若你的 SDK 更新请按官方文档调整。
    video_result = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": f"根据该商品图生成电商短视频脚本：{prompt}"},
                    {"type": "input_image", "image_url": image_url},
                ],
            }
        ],
    )

    # 这里返回脚本建议，实际视频生成可对接你可用的视频模型/服务
    summary = video_result.output_text

    created_at = datetime.utcnow().isoformat()
    rec_id = str(uuid.uuid4())
    records = load_history()
    records.insert(0, {
        "id": rec_id,
        "type": "video_task",
        "image_url": image_url,
        "prompt": prompt,
        "result": summary,
        "created_at": created_at,
    })
    save_history(records)

    return jsonify({"id": rec_id, "result": summary})


@app.route("/api/history")
def history():
    return jsonify(load_history())


@app.route('/outputs/<path:filename>')
def outputs(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
