---
description: 使用即梦 AI 交互编辑 inpainting
argument-hint: <图片URL> [编辑描述]
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 交互编辑 Inpainting

用户参数: $ARGUMENTS

## 前置检查

1. 读取 `~/.jimeng/config.json`，不存在则提示先运行 `/jimeng-setup`
2. `pip install volcengine requests -q 2>/dev/null`

## 流程

### 1. 获取图片 URL
从 $ARGUMENTS 中提取图片 URL，否则询问用户提供原图 URL。

### 2. 获取编辑描述
从 $ARGUMENTS 中提取编辑描述，否则询问用户想要如何修改图片。

### 3. 提交任务
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
    "req_key": "jimeng_image2image_dream_inpaint",
    "prompt": "EDIT_PROMPT",
    "image_urls": ["IMAGE_URL"]
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
