---
description: 使用即梦 AI 交互编辑 inpainting
argument-hint: [编辑描述]
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 交互编辑 Inpainting

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

**如果用户没有提供图片**，使用 AskUserQuestion 提示用户发送图片。

### 2. 获取编辑描述
从 $ARGUMENTS 中提取编辑描述，否则询问用户想要如何修改图片。

### 3. 提交任务（使用 base64 传入本地图片）
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
    "req_key": "jimeng_image2image_dream_inpaint",
    "prompt": "EDIT_PROMPT",
    "image_base64": [image_base64]
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

### 4. 轮询结果（每 3 秒，最多 3 分钟）
查询时附加参数：
```python
form = {
    "req_key": "jimeng_image2image_dream_inpaint",
    "task_id": task_id,
    "req_json": "{\"return_url\":true,\"logo_info\":{\"add_logo\":false}}"
}
```
结果中 `image_urls` 包含编辑后的图片 URL。

### 5. 下载图片
下载到 `~/jimeng-images/jimeng_edit_YYYYMMDD_HHMMSS.png`。

### 6. 报告结果
告知用户：文件路径、文件大小。
