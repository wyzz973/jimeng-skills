---
name: jimeng-ai
description: 即梦 AI 多模态生成。当用户提到"生成视频"、"生成图片"、"文生视频"、"文生图"、"图生视频"、"即梦"、"jimeng"、"AI视频"、"AI图片"、"数字人"、"动作模仿"、"图片超清"、"图片编辑"、"inpainting"、"超分辨率"、"画一张"、"做个视频"、"口播"时使用。通过火山引擎即梦 AI API 生成图片和视频。
version: 2.1.0
metadata:
  openclaw:
    requires:
      bins:
        - python3
      env:
        - JIMENG_AK
        - JIMENG_SK
    primaryEnv: JIMENG_AK
    emoji: "🎬"
---

# 即梦 AI 多模态生成

支持 7 大功能：文生图、文生视频、图生视频、图片编辑、智能超清、数字人、动作模仿。

## 配置

首次使用前检查 `~/.jimeng/config.json` 是否存在。如果不存在，引导用户配置：

1. 告知用户需要火山引擎 AK/SK：登录 https://console.volcengine.com → 右上角账户 → API 访问密钥
2. 告知用户需要开通即梦 AI 服务：https://console.volcengine.com/ai/overview
3. 获取用户的 Access Key 和 Secret Key
4. 保存配置：

```bash
mkdir -p ~/.jimeng && cat > ~/.jimeng/config.json << JSONEOF
{"access_key": "用户的AK", "secret_key": "用户的SK"}
JSONEOF
chmod 600 ~/.jimeng/config.json
```

5. 安装依赖：`pip install volcengine requests -q`

## 功能路由

根据用户意图选择功能：

| 意图 | 功能 | 需要输入 |
|------|------|---------|
| 文字描述生成图片 | 文生图 4.0 | prompt |
| 文字描述生成视频 | 文生视频 3.0 Pro | prompt |
| 图片转视频 | 图生视频 | **图片** + prompt |
| 编辑修改图片 | Inpainting | **图片** + prompt |
| 图片放大增强 | 智能超清 | **图片** |
| 图片+音频做口播 | 数字人 | **图片** + **音频** |
| 图片+视频做动作迁移 | 动作模仿 | **图片** + **视频** |

---

## ⚠️ 用户文件获取（最重要！必须严格执行）

图生视频、图片编辑、智能超清、数字人、动作模仿这 5 个功能都需要用户提供文件（图片/音频/视频）。
本 skill 运行在 OpenClaw + 飞书环境中，用户通过飞书对话发送文件。

**你必须按以下步骤获取文件，不可跳过：**

### 第一步：在对话上下文中查找文件

仔细检查用户消息，查找以下任一形式的文件引用：

1. **本地文件路径**：如 `/tmp/openclaw-feishu-media/xxx.jpg`、`/var/folders/.../xxx.png`、`~/.openclaw/media/xxx.jpg`
2. **URL 链接**：如 `https://...` 开头的图片/音频/视频地址
3. **附件标记**：如 `[Image]`、`[Audio]`、`[Video]` 等标记，可能包含文件路径或描述
4. **用户在对话中粘贴的文件路径**

### 第二步：如果对话中没有找到文件路径

**主动搜索 OpenClaw 媒体目录中最近的文件：**

```bash
# 搜索最近 10 分钟内的图片文件（会搜索 /tmp/openclaw-feishu-media、~/.openclaw/media 等目录）
python3 {baseDir}/scripts/jimeng_helper.py find-media --type image --minutes 10

# 搜索最近的音频文件（用于数字人功能）
python3 {baseDir}/scripts/jimeng_helper.py find-media --type audio --minutes 10

# 搜索最近的视频文件（用于动作模仿功能）
python3 {baseDir}/scripts/jimeng_helper.py find-media --type video --minutes 10
```

返回 JSON 数组，包含 path、modified、size_kb。

如果找到了文件，**必须展示给用户确认**："我找到了以下最近的文件，请确认是否使用这个文件：[文件路径]（大小：xx KB，修改时间：xx）"

### 第三步：如果仍然没有找到文件

**明确告诉用户需要发送文件，并给出具体指引：**

> 我需要你提供一张图片才能继续。请在飞书对话中直接发送图片给我，或者提供图片的 URL 链接 / 本地文件路径。
>
> 支持的格式：JPG、PNG、GIF、WebP

**等待用户发送文件后再继续，不要在没有文件的情况下调用 API。**

### 第四步：处理获取到的文件

拿到文件路径或 URL 后：

**如果是 URL**，先下载到本地：
```bash
python3 {baseDir}/scripts/jimeng_helper.py save-url --url "文件URL" --ext jpg
```
命令会输出保存的本地路径。

**如果是本地路径**，直接使用。

**转换为 base64**（所有需要文件的 API 都用 base64 传入）：
```bash
python3 {baseDir}/scripts/jimeng_helper.py base64 --file "本地文件路径"
```

**重要**：base64 输出可能很长。将其保存到变量或临时文件中使用：
```bash
IMAGE_B64=$(python3 {baseDir}/scripts/jimeng_helper.py base64 --file "本地文件路径")
```

---

## 通用 API 调用流程

### 提交任务

```bash
python3 {baseDir}/scripts/jimeng_helper.py submit --form '{"req_key":"...","prompt":"..."}'
```

从输出的 JSON 中获取 `task_id`。

### 轮询结果

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "REQ_KEY" --task-id "TASK_ID" --max-wait 300
```

### 下载文件

```bash
python3 {baseDir}/scripts/jimeng_helper.py download --url "FILE_URL" --dir "~/jimeng-videos" --prefix "jimeng" --ext "mp4"
```

---

## 各功能详细流程

### 1. 文生图 4.0

**不需要文件输入，只需要文字描述。**

1. 获取用户描述
2. **AI 优化提示词**：补充画面细节、构图、光影、色彩、风格，不超过 300 字。展示给用户确认
3. 提交任务：

```bash
python3 {baseDir}/scripts/jimeng_helper.py submit --form '{"req_key":"jimeng_t2i_v40","prompt":"优化后提示词","seed":-1}'
```

4. 轮询结果（interval=3, max_wait=180）：

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "jimeng_t2i_v40" --task-id "TASK_ID" --max-wait 180 --interval 3
```

5. 从结果 JSON 的 `data.image_urls` 取 URL，下载图片：

```bash
python3 {baseDir}/scripts/jimeng_helper.py download --url "图片URL" --dir "~/jimeng-images" --prefix "jimeng" --ext "png"
```

6. 告知用户文件路径和大小

### 2. 文生视频 3.0 Pro

**不需要文件输入，只需要文字描述。**

1. 获取用户描述
2. **AI 优化提示词**：补充运动描述、镜头语言、氛围，不超过 400 字。展示给用户确认
3. 询问参数：分辨率(720p/1080p)、时长(5秒/10秒)、比例(16:9/9:16/1:1/4:3/3:4/21:9)
4. 确定 req_key：720p→`jimeng_t2v_v30`，1080p→`jimeng_t2v_v30_1080p`
5. 提交：

```bash
python3 {baseDir}/scripts/jimeng_helper.py submit --form '{"req_key":"jimeng_t2v_v30","prompt":"优化后提示词","seed":-1,"frames":121,"aspect_ratio":"16:9"}'
```

frames: 121=5秒, 241=10秒

6. 轮询结果（interval=5, max_wait=300）：

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "REQ_KEY" --task-id "TASK_ID" --max-wait 300 --interval 5
```

7. 从结果下载视频：

```bash
python3 {baseDir}/scripts/jimeng_helper.py download --url "视频URL" --dir "~/jimeng-videos" --prefix "jimeng" --ext "mp4"
```

### 3. 图生视频

**⚠️ 需要用户提供图片！必须先执行「用户文件获取」流程获取图片文件。**

完整步骤：

1. **获取图片文件**：按照上方「用户文件获取」流程，从对话中找到图片路径/URL，下载并转为 base64：

```bash
# 如果是 URL，先下载
python3 {baseDir}/scripts/jimeng_helper.py save-url --url "图片URL" --ext jpg
# 转 base64（替换为实际本地路径）
IMAGE_B64=$(python3 {baseDir}/scripts/jimeng_helper.py base64 --file "本地图片路径")
```

2. 获取用户对视频的描述 → AI 优化提示词 → 展示给用户确认
3. 询问：分辨率(720p/1080p)、时长(5s/10s)、是否运镜(仅720p)
4. 提交任务（将 base64 直接嵌入 form 的 JSON 中）：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("本地图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_i2v_first_v30",
    "prompt": "优化后的提示词",
    "image_base64": [image_b64],
    "seed": -1,
    "frames": 121
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

5. 从输出获取 task_id，轮询结果：

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "jimeng_i2v_first_v30" --task-id "TASK_ID" --max-wait 300 --interval 5
```

6. 下载视频到 `~/jimeng-videos/`，prefix=`jimeng_i2v`

运镜模式改用 `jimeng_i2v_recamera_v30`，form 中额外加 `template_id` 和 `camera_strength`（weak/medium/strong）。

### 4. 图片编辑 Inpainting

**⚠️ 需要用户提供图片！必须先执行「用户文件获取」流程获取图片文件。**

完整步骤：

1. **获取图片文件**：按照「用户文件获取」流程获取图片并转 base64：

```bash
# 如果是 URL，先下载
python3 {baseDir}/scripts/jimeng_helper.py save-url --url "图片URL" --ext jpg
# 转 base64
IMAGE_B64=$(python3 {baseDir}/scripts/jimeng_helper.py base64 --file "本地图片路径")
```

2. 获取用户的编辑描述（如"把背景换成海边"）

3. 提交任务：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("本地图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_image2image_dream_inpaint",
    "prompt": "编辑描述",
    "image_base64": [image_b64]
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

4. 轮询时查询 form 需要附加 `req_json`：

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
    "task_id": "TASK_ID",
    "req_json": "{\"return_url\":true,\"logo_info\":{\"add_logo\":false}}"
}
resp = vs.cv_sync2async_get_result(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

重复查询直到 `data.image_urls` 出现或失败。

5. 从 `data.image_urls` 下载到 `~/jimeng-images/`，prefix=`jimeng_edit`，ext=`png`

### 5. 智能超清

**⚠️ 需要用户提供图片！必须先执行「用户文件获取」流程获取图片文件。**

完整步骤：

1. **获取图片文件**：按照「用户文件获取」流程获取图片并转 base64：

```bash
python3 {baseDir}/scripts/jimeng_helper.py save-url --url "图片URL" --ext jpg
IMAGE_B64=$(python3 {baseDir}/scripts/jimeng_helper.py base64 --file "本地图片路径")
```

2. 提交任务：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("本地图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_high_aes_general_v21_L",
    "image_base64": [image_b64]
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

3. 轮询结果：

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "jimeng_high_aes_general_v21_L" --task-id "TASK_ID" --max-wait 180 --interval 3
```

4. 从 `data.image_urls` 下载到 `~/jimeng-images/`，prefix=`jimeng_hd`，ext=`png`

### 6. 数字人（两步）

**⚠️ 需要用户提供图片和音频！必须先执行「用户文件获取」流程分别获取两个文件。**

完整步骤：

1. **获取人物图片**：按照「用户文件获取」流程获取图片。
   - 图片要求：JPG/PNG, <5MB, **必须是单人正面清晰照片**
   - 如果用户没有发送图片，明确告诉用户：
   > 请发送一张人物正面照片（JPG/PNG，< 5MB，单人正面，面部清晰无遮挡）

2. **获取音频文件**：同样按照「用户文件获取」流程获取音频。
   - 音频要求：时长 < 15秒
   - 如果用户没有发送音频，明确告诉用户：
   > 请发送一段音频文件（时长不超过15秒），作为数字人的口播内容

3. **步骤1 主体识别**（同步调用）：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("本地图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_realman_avatar_picture_create_role_omni",
    "image_base64": image_b64
}
resp = vs.cv_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

确认 code=10000 且 status=1。如果失败（如 50218 安全检查），提示用户换一张正面清晰无遮挡的人物图片。

4. **步骤2 视频生成**：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("本地图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")
with open("本地音频路径", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_realman_avatar_picture_omni_v2",
    "image_base64": image_b64,
    "audio_base64": audio_b64
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

5. 轮询结果 → 下载到 `~/jimeng-videos/`，prefix=`jimeng_dh`，ext=`mp4`
6. 输出为 480P MP4 视频

### 7. 动作模仿 2.0

**⚠️ 需要用户提供图片和视频！必须先执行「用户文件获取」流程分别获取两个文件。**

完整步骤：

1. **获取人物图片**：按照「用户文件获取」流程获取图片。
   - 图片要求：JPEG/PNG, 480x480~1920x1080, < 4.7MB
   - 如果用户没有发送图片，明确告诉用户：
   > 请发送一张人物图片（JPEG/PNG，< 4.7MB）

2. **获取模板视频**：同样按照「用户文件获取」流程获取视频。
   - 视频要求：MP4/MOV/WebM, ≤ 30秒
   - 如果用户没有发送视频，明确告诉用户：
   > 请发送一段动作参考视频（MP4/MOV/WebM，不超过30秒）

3. 提交任务：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("本地图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")
with open("本地视频路径", "rb") as f:
    video_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_motion_imitation_v2",
    "image_base64": image_b64,
    "video_base64": video_b64
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

4. 轮询（max_wait=600, interval=5，处理较慢，约 3 分钟+）：

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "jimeng_motion_imitation_v2" --task-id "TASK_ID" --max-wait 600 --interval 5
```

5. 下载到 `~/jimeng-videos/`，prefix=`jimeng_motion`，ext=`mp4`
6. 输出为 720P 25fps MP4

---

## 提示词优化策略

优化用户的原始提示词时：
- **文生图**：补充构图、光影、色彩、质感、风格基调
- **文生视频**：补充镜头运动（推拉摇移）、物体运动、氛围节奏
- 展示原始和优化后的版本，让用户确认或修改
- 保持简洁，文生图不超过 300 字，文生视频不超过 400 字

## 错误处理

| 场景 | 处理 |
|------|------|
| 未配置密钥 | 引导配置 ~/.jimeng/config.json |
| API 认证失败 | 提示检查 AK/SK |
| 50218 安全检查 | 提示换正面清晰无遮挡图片 |
| 余额不足 | 提示充值火山引擎 |
| 超时 | 提供 task_id 供手动查询 |
| 下载失败 | 提供 URL 供手动下载 |
| **找不到用户文件** | **主动搜索 OpenClaw 媒体目录，或明确要求用户重新发送文件** |

## 详细 API 参考

见 [api-reference.md](references/api-reference.md)
