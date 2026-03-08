---
description: 使用即梦 AI 动作模仿 2.0（图片+视频生成动作迁移视频）
argument-hint: <图片URL> <模板视频URL>
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 动作模仿 2.0

用户参数: $ARGUMENTS

## 前置检查

1. 读取 `~/.jimeng/config.json`，不存在则提示先运行 `/jimeng-setup`
2. `pip install volcengine requests -q 2>/dev/null`

## 流程

### 1. 获取输入
- **图片 URL**：人物图片（JPEG/PNG，480x480~1920x1080，< 4.7MB）
- **模板视频 URL**：动作参考视频（MP4/MOV/WebM，≤ 30 秒）

从 $ARGUMENTS 中提取，否则逐一询问用户。

### 2. 提交任务
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
    "req_key": "jimeng_motion_imitation_v2",
    "image_url": "IMAGE_URL",
    "video_url": "VIDEO_URL"
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

### 3. 轮询结果（每 5 秒，最多 10 分钟）
处理较慢（RTF ~18，10 秒视频约需 180 秒），结果中 `video_url` 即为生成视频。输出为 720P 25fps MP4。

### 4. 下载视频
下载到 `~/jimeng-videos/jimeng_motion_YYYYMMDD_HHMMSS.mp4`。

### 5. 报告结果
告知用户：文件路径、文件大小。
