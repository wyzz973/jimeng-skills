---
description: 使用即梦 AI 数字人快速模式（图片+音频生成口播视频）
argument-hint: <图片URL> <音频URL>
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 数字人快速模式

用户参数: $ARGUMENTS

## 前置检查

1. 读取 `~/.jimeng/config.json`，不存在则提示先运行 `/jimeng-setup`
2. `pip install volcengine requests -q 2>/dev/null`

## 流程

### 1. 获取输入
- **图片 URL**：人物照片（JPG/PNG，< 5MB，建议单人正面）
- **音频 URL**：配音音频（建议 < 15 秒）

从 $ARGUMENTS 中提取，否则逐一询问用户。

### 2. 步骤一：主体识别
确认图片中存在有效的人物主体：

```bash
python3 << 'PYEOF'
import json, os, time
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

# 提交主体识别
form = {
    "req_key": "jimeng_realman_avatar_picture_create_role_omni",
    "image_url": "IMAGE_URL"
}
resp = vs.cv_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

检查返回结果，确认 code=10000 且 status=1（识别到有效主体）。如果识别失败，提示用户换一张更清晰的正面人物图。

### 3. 步骤二：视频生成
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
    "req_key": "jimeng_realman_avatar_picture_omni_v2",
    "image_url": "IMAGE_URL",
    "audio_url": "AUDIO_URL"
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

### 4. 轮询结果（每 5 秒，最多 5 分钟）
结果中 `video_url` 即为数字人视频。输出为 480P MP4。

### 5. 下载视频
下载到 `~/jimeng-videos/jimeng_dh_YYYYMMDD_HHMMSS.mp4`。

### 6. 报告结果
告知用户：文件路径、文件大小。
