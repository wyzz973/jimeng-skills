---
description: 使用即梦 AI 图生视频
argument-hint: [提示词]
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 图生视频

用户参数: $ARGUMENTS

## 前置检查

1. 读取 `~/.jimeng/config.json`，不存在则提示先运行 `/jimeng-setup`
2. `pip install volcengine requests -q 2>/dev/null`

## 流程

### 1. 获取图片

用户通过飞书对话发送图片。你需要：

1. **识别图片来源**：检查对话中是否有用户发送的图片文件（本地路径或 URL）
2. **保存到本地**：将图片保存到 `~/jimeng-images/input/` 目录

```bash
mkdir -p ~/jimeng-images/input
```

**如果是本地文件路径**（如 `/tmp/xxx.jpg` 或用户指定的路径），直接使用该路径。

**如果是 URL**，先下载到本地：
```bash
python3 << 'PYEOF'
import requests, os, time
url = "IMAGE_URL"
save_dir = os.path.expanduser("~/jimeng-images/input")
os.makedirs(save_dir, exist_ok=True)
filename = f"input_{int(time.time())}.jpg"
filepath = os.path.join(save_dir, filename)
r = requests.get(url)
with open(filepath, "wb") as f:
    f.write(r.content)
print(filepath)
PYEOF
```

**如果用户没有提供图片**，使用 AskUserQuestion 提示用户发送图片。

### 2. 获取并优化提示词
获取用户对视频效果的描述，AI 优化后展示给用户确认。

### 3. 选择参数
使用 AskUserQuestion 询问：
- 分辨率：720p / 1080p
- 时长：5 秒 / 10 秒
- 是否使用运镜（仅 720p）

### 4. 提交任务（使用 base64 传入本地图片）

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

# 读取本地图片并转为 base64
image_path = "LOCAL_IMAGE_PATH"
with open(image_path, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "REQ_KEY",  # jimeng_i2v_first_v30(720p) / jimeng_i2v_first_v30_1080(1080p)
    "prompt": "PROMPT",
    "image_base64": [image_base64],
    "seed": -1,
    "frames": FRAMES  # 121=5s, 241=10s
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

**运镜模式（仅 720p）：**
req_key 使用 `jimeng_i2v_recamera_v30`，额外参数：
- `template_id`: 运镜模板（如 `hitchcock_dolly_in`）
- `camera_strength`: 运镜强度（`weak`/`medium`/`strong`）

### 5. 轮询结果（每 5 秒，最多 5 分钟）

### 6. 下载视频
下载到 `~/jimeng-videos/jimeng_i2v_YYYYMMDD_HHMMSS.mp4`。

### 7. 报告结果
告知用户：文件路径、文件大小。

## req_key 参考
| 场景 | req_key |
|------|---------|
| 首帧图生视频 720p | `jimeng_i2v_first_v30` |
| 首帧图生视频 1080p | `jimeng_i2v_first_v30_1080` |
| 720p 运镜 | `jimeng_i2v_recamera_v30` |
