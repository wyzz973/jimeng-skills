---
name: jimeng-video
description: 当用户提到"生成视频"、"做一个视频"、"文生视频"、"即梦"、"jimeng"、"AI视频"、"视频生成"、"帮我生成一段视频"、"创建视频"等与 AI 视频生成相关的请求时，自动触发此 skill。使用火山引擎即梦 AI API 将用户的文本描述生成为视频。
version: 1.0.0
---

# 即梦 AI 文生视频 Skill

当检测到用户有视频生成需求时，自动执行以下流程。

## 前置条件检查

1. **检查配置文件** `~/.jimeng/config.json` 是否存在
   - 如果不存在，引导用户使用 `/jimeng-setup` 命令配置 Access Key 和 Secret Key
   - 如果存在，读取其中的 `access_key` 和 `secret_key`

2. **检查 Python 依赖**
   ```bash
   pip install volcengine requests -q 2>/dev/null
   ```

## 执行流程

### Step 1: 获取用户意图

从用户消息中提取视频描述意图。如果描述不够清晰，使用 AskUserQuestion 询问用户想要生成什么样的视频。

### Step 2: 优化提示词

作为大模型，根据以下原则优化用户的提示词：

**优化策略：**
- 补充视觉细节：画面构图、光影、色彩、质感
- 添加运动描述：镜头运动（推、拉、摇、移）、物体运动
- 指定风格基调：电影质感、动画风格、写实、梦幻等
- 氛围渲染：情感基调、音乐感、节奏感
- 控制长度：优化后不超过 400 字

向用户展示原始提示词和优化后的提示词，让用户确认或修改。

### Step 3: 选择视频参数

使用 AskUserQuestion 让用户选择：

1. **分辨率**：720p（更快） / 1080p（更清晰）
2. **时长**：5 秒 / 10 秒
3. **画面比例**：16:9 / 9:16 / 1:1 / 4:3 / 3:4 / 21:9

### Step 4: 提交生成任务

根据选择确定参数：
- 分辨率 → req_key: `jimeng_t2v_v30`(720p) 或 `jimeng_t2v_v30_1080p`(1080p)
- 时长 → frames: `121`(5秒) 或 `241`(10秒)

调用火山引擎 SDK：

```python
from volcengine.visual.VisualService import VisualService
import json

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)

vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

form = {
    "req_key": req_key,
    "prompt": optimized_prompt,
    "seed": -1,
    "frames": frames,
    "aspect_ratio": aspect_ratio
}
resp = vs.cv_sync2async_submit_task(form)
task_id = resp["data"]["task_id"]
```

### Step 5: 轮询等待结果

告知用户"视频生成中，预计需要 1-3 分钟..."

每 5 秒查询一次任务状态，最多等待 5 分钟：

```python
form = {
    "req_key": req_key,
    "task_id": task_id
}
resp = vs.cv_sync2async_get_result(form)
```

检查返回结果中的状态，直到任务完成或失败。

### Step 6: 下载视频

从返回结果中提取 `video_url`，下载到 `~/jimeng-videos/` 目录：

```bash
mkdir -p ~/jimeng-videos
```

文件命名格式：`jimeng_YYYYMMDD_HHMMSS.mp4`

### Step 7: 报告结果

向用户展示：
- 生成成功的消息
- 本地文件路径（绝对路径）
- 文件大小
- 使用的提示词（优化后版本）

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 未配置密钥 | 引导使用 `/jimeng-setup` |
| API 认证失败 | 提示检查 AK/SK 是否正确 |
| 余额不足 | 提示充值火山引擎账户 |
| 参数错误 | 解析错误信息并修正 |
| 生成超时 | 提供 task_id 供手动查询 |
| 下载失败 | 提供视频 URL 供手动下载 |

## API 参考

- **提交任务**: `VisualService.cv_sync2async_submit_task(form)`
- **查询结果**: `VisualService.cv_sync2async_get_result(form)`
- **文生视频 720p req_key**: `jimeng_t2v_v30`
- **文生视频 1080p req_key**: `jimeng_t2v_v30_1080p`
- **5 秒视频**: `frames=121`
- **10 秒视频**: `frames=241`
- **支持比例**: `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, `21:9`
