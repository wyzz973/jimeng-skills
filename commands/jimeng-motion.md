---
description: 使用即梦 AI 动作模仿 2.0（图片+视频生成动作迁移视频）
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 动作模仿 2.0

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

**图片要求**：JPEG/PNG，480x480~1920x1080，< 4.7MB。

### 2. 获取模板视频

用户可能通过飞书发送视频文件，或提供视频 URL。

**如果用户发送了视频文件**，同样保存到本地 `~/jimeng-images/input/`。

**如果是 URL**，先下载到本地。

**如果用户没有提供视频**，使用 AskUserQuestion 提示用户发送动作参考视频。

**视频要求**：MP4/MOV/WebM，≤ 30 秒，200x200~2048x1440。

### 3. 提交任务（使用 base64 传入本地文件）
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

# 读取本地视频
video_path = "LOCAL_VIDEO_PATH"
with open(video_path, "rb") as f:
    video_base64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_motion_imitation_v2",
    "image_base64": image_base64,
    "video_base64": video_base64
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

### 4. 轮询结果（每 5 秒，最多 10 分钟）
处理较慢（RTF ~18，10 秒视频约需 180 秒），结果中 `video_url` 即为生成视频。输出为 720P 25fps MP4。

### 5. 下载视频
下载到 `~/jimeng-videos/jimeng_motion_YYYYMMDD_HHMMSS.mp4`。

### 6. 报告结果
告知用户：文件路径、文件大小。
