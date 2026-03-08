---
description: 使用即梦 AI 4.0 文生图
argument-hint: [提示词]
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 文生图 4.0

用户参数: $ARGUMENTS

## 前置检查

1. 读取 `~/.jimeng/config.json`，不存在则提示先运行 `/jimeng-setup`
2. `pip install volcengine requests -q 2>/dev/null`

## 流程

### 1. 获取提示词
如果 $ARGUMENTS 中有提示词则使用，否则询问用户想要生成什么图片。

### 2. 优化提示词
补充画面细节（构图、光影、色彩、质感、风格），不超过 300 字。展示给用户确认。

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
    "req_key": "jimeng_t2i_v40",
    "prompt": "PROMPT",
    "seed": -1
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

### 4. 轮询结果（每 3 秒，最多 3 分钟）
```bash
python3 << 'PYEOF'
import json, os, time
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

for i in range(60):
    resp = vs.cv_sync2async_get_result({"req_key": "jimeng_t2i_v40", "task_id": "TASK_ID"})
    data = resp.get("data", {})
    if data.get("status") == "done" or data.get("image_urls"):
        print(json.dumps(resp, ensure_ascii=False, indent=2))
        break
    if "fail" in str(data.get("status", "")).lower():
        print(json.dumps(resp, ensure_ascii=False, indent=2))
        break
    time.sleep(3)
else:
    print(json.dumps({"error": "超时", "task_id": "TASK_ID"}))
PYEOF
```

### 5. 下载图片
从结果的 `image_urls` 中下载所有图片到 `~/jimeng-images/jimeng_YYYYMMDD_HHMMSS_N.png`。

### 6. 报告结果
告知用户：文件路径、文件大小、使用的提示词。
