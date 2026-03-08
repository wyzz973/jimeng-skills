---
description: 使用即梦 AI 智能超清（图片放大增强）
argument-hint: <图片URL>
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 智能超清

用户参数: $ARGUMENTS

## 前置检查

1. 读取 `~/.jimeng/config.json`，不存在则提示先运行 `/jimeng-setup`
2. `pip install volcengine requests -q 2>/dev/null`

## 流程

### 1. 获取图片 URL
从 $ARGUMENTS 中提取图片 URL，否则询问用户提供需要增强的图片 URL。

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
    "req_key": "jimeng_high_aes_general_v21_L",
    "image_urls": ["IMAGE_URL"]
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

### 3. 轮询结果（每 3 秒，最多 3 分钟）
结果中 `image_urls` 包含超清图片 URL。

### 4. 下载图片
下载到 `~/jimeng-images/jimeng_hd_YYYYMMDD_HHMMSS.png`。

### 5. 报告结果
告知用户：文件路径、文件大小、原图与增强后的分辨率对比。
