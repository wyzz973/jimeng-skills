---
description: 使用即梦 AI 数字人快速模式（图片+音频生成口播视频）
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 数字人快速模式

用户参数: $ARGUMENTS

## 前置检查

1. 读取 `~/.jimeng/config.json`，不存在则提示先运行 `/jimeng-setup`
2. `pip install volcengine requests -q 2>/dev/null`

## 流程

### 1. 获取图片

用户通过飞书对话发送人物图片。你需要：

1. **识别图片来源**：检查对话中是否有用户发送的图片文件（本地路径或 URL）
2. **保存到本地**：将图片保存到 `~/jimeng-images/input/` 目录

```bash
mkdir -p ~/jimeng-images/input
```

**如果是本地文件路径**，直接使用该路径。

**如果是 URL**，先下载到本地：
```bash
python3 << 'PYEOF'
import requests, os, time
url = "IMAGE_URL"
save_dir = os.path.expanduser("~/jimeng-images/input")
os.makedirs(save_dir, exist_ok=True)
filepath = os.path.join(save_dir, f"input_{int(time.time())}.jpg")
r = requests.get(url)
with open(filepath, "wb") as f:
    f.write(r.content)
print(filepath)
PYEOF
```

**如果用户没有提供图片**，使用 AskUserQuestion 提示用户发送人物图片。

**图片要求**：JPG/PNG，< 5MB，建议单人正面、五官清晰、无遮挡、表情自然。

### 2. 获取音频

用户可能通过飞书发送音频文件，或提供文字让系统生成语音。

**如果用户发送了音频文件**，同样保存到本地 `~/jimeng-images/input/`。

**如果用户提供了文字内容**（如"新年快乐"），需要先生成语音文件（可用系统 TTS 或提示用户提供音频 URL）。

音频建议 < 15 秒。

### 3. 步骤一：主体识别（使用 base64 传入本地图片）

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
    "req_key": "jimeng_realman_avatar_picture_create_role_omni",
    "image_base64": image_base64
}
resp = vs.cv_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

检查返回结果，确认 code=10000 且 status=1（识别到有效主体）。如果识别失败，提示用户换一张更清晰的正面人物图。

### 4. 步骤二：视频生成（使用 base64 传入图片和音频）
```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

# 读取本地图片
image_path = "LOCAL_IMAGE_PATH"
with open(image_path, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# 读取本地音频
audio_path = "LOCAL_AUDIO_PATH"
with open(audio_path, "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_realman_avatar_picture_omni_v2",
    "image_base64": image_base64,
    "audio_base64": audio_base64
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

### 5. 轮询结果（每 5 秒，最多 5 分钟）
结果中 `video_url` 即为数字人视频。输出为 480P MP4。

### 6. 下载视频
下载到 `~/jimeng-videos/jimeng_dh_YYYYMMDD_HHMMSS.mp4`。

### 7. 报告结果
告知用户：文件路径、文件大小。
