---
description: 使用即梦 AI 生成视频
argument-hint: [提示词]
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 文生视频

用户参数: $ARGUMENTS

## 前置检查

### 1. 检查配置

读取 `~/.jimeng/config.json`，如果不存在，提示用户先运行 `/jimeng-setup` 配置密钥。

### 2. 检查依赖

```bash
pip install volcengine requests -q 2>/dev/null
```

## 核心流程

### 3. 获取提示词

如果用户在 $ARGUMENTS 中提供了提示词，使用该提示词。否则使用 AskUserQuestion 询问用户想要生成什么视频。

### 4. 优化提示词

作为大模型，你需要帮助用户优化提示词，使其更适合视频生成。优化原则：

- **视觉描述丰富化**：添加画面构图、光影效果、色彩氛围等细节
- **运动描述**：描述画面中元素的运动方式和镜头运动
- **风格指定**：如电影质感、动画风格、纪录片等
- **保持简洁**：优化后不超过 400 字

向用户展示优化后的提示词，询问是否满意，或者用户可以修改。

### 5. 选择视频参数

使用 AskUserQuestion 询问用户：

**分辨率：**
- 720p（生成更快）
- 1080p（画质更高）

**视频时长：**
- 5 秒（frames=121）
- 10 秒（frames=241）

**画面比例：**
- 16:9（横屏，适合电影/风景）
- 9:16（竖屏，适合手机/短视频）
- 1:1（方形，适合社交媒体）
- 4:3（经典比例）
- 3:4（竖屏经典）
- 21:9（超宽屏，电影感）

### 6. 提交视频生成任务

根据用户选择的分辨率确定 req_key：
- 720p → `jimeng_t2v_v30`
- 1080p → `jimeng_t2v_v30_1080p`

使用 Bash 执行以下 Python 脚本提交任务：

```bash
python3 << 'PYTHON_SCRIPT'
import json
from volcengine.visual.VisualService import VisualService

with open("$HOME/.jimeng/config.json") as f:
    config = json.load(f)

vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

form = {
    "req_key": "REQ_KEY_VALUE",
    "prompt": "OPTIMIZED_PROMPT",
    "seed": -1,
    "frames": FRAMES_VALUE,
    "aspect_ratio": "ASPECT_RATIO_VALUE"
}

resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYTHON_SCRIPT
```

用实际值替换占位符（REQ_KEY_VALUE、OPTIMIZED_PROMPT、FRAMES_VALUE、ASPECT_RATIO_VALUE）。

从返回结果中提取 `task_id`。如果提交失败，解析错误信息告知用户。

### 7. 轮询任务结果

告知用户"视频正在生成中，请稍候..."

使用 Bash 执行轮询脚本（设置合理的超时时间，如 5 分钟）：

```bash
python3 << 'PYTHON_SCRIPT'
import json
import time
from volcengine.visual.VisualService import VisualService

with open("$HOME/.jimeng/config.json") as f:
    config = json.load(f)

vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

task_id = "TASK_ID_VALUE"
req_key = "REQ_KEY_VALUE"
max_attempts = 60
interval = 5

for i in range(max_attempts):
    form = {
        "req_key": req_key,
        "task_id": task_id
    }
    resp = vs.cv_sync2async_get_result(form)
    resp_data = resp.get("data", {})

    # 检查任务状态
    status = resp_data.get("status", "")
    if status == "done" or resp_data.get("resp_data"):
        print(json.dumps(resp, ensure_ascii=False, indent=2))
        break
    elif "fail" in str(status).lower() or "error" in str(resp).lower():
        print(json.dumps(resp, ensure_ascii=False, indent=2))
        break

    if i < max_attempts - 1:
        time.sleep(interval)
else:
    print(json.dumps({"error": "任务超时，请稍后使用 task_id 手动查询", "task_id": task_id}))
PYTHON_SCRIPT
```

### 8. 下载视频到本地

从返回结果中提取视频 URL（通常在 `resp_data` 或 `data` 中的 `video_url` 或类似字段）。

创建保存目录并下载：

```bash
mkdir -p ~/jimeng-videos
python3 << 'PYTHON_SCRIPT'
import requests
import os
from datetime import datetime

video_url = "VIDEO_URL_HERE"
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"jimeng_{timestamp}.mp4"
filepath = os.path.expanduser(f"~/jimeng-videos/{filename}")

response = requests.get(video_url, stream=True)
with open(filepath, "wb") as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

file_size = os.path.getsize(filepath)
print(f"视频已保存: {filepath}")
print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
PYTHON_SCRIPT
```

### 9. 告知用户结果

向用户报告：
- 视频已成功生成并保存
- 本地文件路径
- 文件大小
- 使用的提示词和参数

## 错误处理

- **配置不存在**：提示运行 `/jimeng-setup`
- **API 调用失败**：解析错误码，给出建议（如余额不足、参数错误等）
- **任务超时**：提供 task_id，告知用户可以稍后查询
- **下载失败**：提供视频 URL，让用户手动下载
