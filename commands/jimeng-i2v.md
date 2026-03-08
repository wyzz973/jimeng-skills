---
description: 使用即梦 AI 图生视频
argument-hint: <图片URL> [提示词]
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 图生视频

用户参数: $ARGUMENTS

## 前置检查

1. 读取 `~/.jimeng/config.json`，不存在则提示先运行 `/jimeng-setup`
2. `pip install volcengine requests -q 2>/dev/null`

## 流程

### 1. 获取图片 URL
从 $ARGUMENTS 中提取图片 URL，否则询问用户提供图片 URL。

### 2. 获取并优化提示词
获取用户对视频效果的描述，AI 优化后展示给用户确认。

### 3. 选择参数
使用 AskUserQuestion 询问：
- 分辨率：720p / 1080p
- 时长：5 秒 / 10 秒
- 是否使用运镜（仅 720p）

### 4. 提交任务

**普通模式：**
```bash
python3 << 'PYEOF'
import json, os
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

form = {
    "req_key": "REQ_KEY",  # jimeng_i2v_first_v30(720p) / jimeng_i2v_first_v30_1080(1080p)
    "prompt": "PROMPT",
    "image_urls": ["IMAGE_URL"],
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
