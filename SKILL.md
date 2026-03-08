---
name: jimeng-ai
description: 即梦 AI 多模态生成。当用户提到"生成视频"、"生成图片"、"文生视频"、"文生图"、"图生视频"、"即梦"、"jimeng"、"AI视频"、"AI图片"、"数字人"、"动作模仿"、"图片超清"、"图片编辑"、"inpainting"、"超分辨率"、"画一张"、"做个视频"、"口播"时使用。通过火山引擎即梦 AI API 生成图片和视频。
version: 2.3.0
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

| 意图 | 功能 | 需要文件 |
|------|------|---------|
| 文字描述生成图片 | 文生图 4.0 | 无 |
| 文字描述生成视频 | 文生视频 3.0 Pro | 无 |
| 图片转视频 | 图生视频 | **图片** |
| 编辑修改图片 | Inpainting | **图片** |
| 图片放大增强 | 智能超清 | **图片** |
| 图片+音频做口播 | 数字人 | **图片 + 音频** |
| 图片+视频做动作迁移 | 动作模仿 | **图片 + 视频** |

---

## ⚠️⚠️⚠️ 严禁事项（必读）

1. **严禁将 base64 字符串通过命令行参数传递！** base64 字符串非常长（100KB+），放在 shell 命令参数里会被截断/损坏，导致 API 收到损坏的图片。所有需要传文件的 API 调用，**必须使用 inline Python 脚本**（`python3 << 'PYEOF'`），在脚本内部读取文件并 base64 编码后直接调用 SDK。
2. **严禁跳过提示词优化步骤！** 必须先 AI 优化提示词，展示给用户确认后再提交任务。
3. **严禁在没有获取到文件的情况下调用需要文件的 API！** 如果找不到用户的文件，必须停下来要求用户重新发送。
4. **严禁混淆 API 参数名！** 不同的即梦 API 使用不同的参数名传图片/视频：
   - **图生视频**必须用 `binary_data_base64`（不是 `image_base64`！）
   - **动作模仿**的视频必须用 `binary_data_base64`（不是 `video_base64`！）
   - **数字人**用 `image_base64`（字符串，不是数组！）
   - 详见各功能代码示例中的参数名，**必须严格照抄参数名**，否则 API 会静默忽略你的文件！

---

## 用户文件获取流程

图生视频、图片编辑、智能超清、数字人、动作模仿这 5 个功能需要用户提供文件。
用户通过飞书对话发送的文件存储在 `~/.openclaw/media/inbound/` 目录中，文件名为 UUID 格式。

### 步骤 1：在对话上下文中查找文件路径

检查用户消息中是否有：
- 本地文件路径（如 `/Users/sd3/.openclaw/media/inbound/xxx.jpg`）
- URL（`https://...`）
- `[Image]`、`[Audio]`、`[Video]` 附件标记

### 步骤 2：搜索 inbound 目录

如果对话中没有明确的文件路径：

```bash
ls -lt ~/.openclaw/media/inbound/ | head -5
```

找到最新的文件后，展示给用户确认："找到了这个文件：[路径]，是否使用？"

### 步骤 3：要求用户发送

如果仍然找不到，告诉用户：
> 我需要你的图片/音频/视频文件。请在飞书对话中直接发送给我。

**拿到文件后不要调用 base64 命令行工具！** 直接在 inline Python 脚本中读取文件。

---

## 提示词优化（必须执行）

每次生成前必须优化用户的原始描述：

**文生图**：补充构图、光影、色彩、质感、风格基调，不超过 300 字
**文生视频/图生视频**：补充镜头运动（推拉摇移）、物体运动、氛围节奏，不超过 400 字

展示格式：
> **原始描述**：用户原文
> **优化后**：优化后的提示词
> 请确认是否OK？确认后开始生成。

**必须等用户确认后再提交任务。**

---

## 结果发送

视频/图片生成完成后：

1. 先用 helper 脚本下载到本地
2. 发送视频到飞书时使用 `msg_type: "media"`（不是 "file"！）：

```
message tool: action=send, filePath=本地视频路径, msg_type=media, receive_id=用户ID, receive_id_type=open_id
```

如果发送失败，告知用户本地文件路径供手动获取。

---

## 各功能完整流程

### 1. 文生图 4.0

不需要文件，只需文字描述。

1. 获取用户描述 → **AI 优化提示词** → 展示给用户确认
2. 用户确认后，提交任务：

```bash
python3 {baseDir}/scripts/jimeng_helper.py submit --form '{"req_key":"jimeng_t2i_v40","prompt":"优化后提示词","seed":-1}'
```

3. 从输出获取 task_id，轮询结果：

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "jimeng_t2i_v40" --task-id "TASK_ID" --max-wait 180 --interval 3
```

4. 从结果 `data.image_urls` 下载图片：

```bash
python3 {baseDir}/scripts/jimeng_helper.py download --url "图片URL" --dir "~/jimeng-images" --prefix "jimeng" --ext "png"
```

5. 将图片发送给用户并告知路径

### 2. 文生视频 3.0 Pro

不需要文件，只需文字描述。

1. 获取用户描述 → **AI 优化提示词** → 展示给用户确认
2. 询问参数：分辨率(720p/1080p)、时长(5秒/10秒)、比例(16:9/9:16/1:1/4:3/3:4/21:9)
3. 确定 req_key：720p→`jimeng_t2v_v30`，1080p→`jimeng_t2v_v30_1080p`
4. frames：121=5秒, 241=10秒
5. 提交：

```bash
python3 {baseDir}/scripts/jimeng_helper.py submit --form '{"req_key":"jimeng_t2v_v30","prompt":"优化后提示词","seed":-1,"frames":121,"aspect_ratio":"16:9"}'
```

6. 轮询（interval=5, max_wait=300）→ 下载视频 → 发送给用户

### 3. 图生视频

**需要用户图片。按「用户文件获取流程」获取图片的本地路径。**

1. 获取图片本地路径（如 `~/.openclaw/media/inbound/xxx.jpg`）
2. 获取用户描述 → **AI 优化提示词** → 展示给用户确认
3. 询问：分辨率(720p/1080p)、时长(5s/10s)
4. 用户确认后，**用 inline Python 提交**（严禁通过命令行传 base64）：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

# 在脚本内部读取图片并编码，绝不通过命令行传递 base64
with open("此处替换为图片的完整本地路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

# ⚠️ 图生视频必须用 binary_data_base64，不是 image_base64！
form = {
    "req_key": "jimeng_i2v_first_v30",  # 720p；1080p 用 jimeng_i2v_first_v30_1080
    "prompt": "此处替换为优化后的提示词",
    "binary_data_base64": [image_b64],  # 注意：必须是 binary_data_base64，不是 image_base64！
    "seed": -1,
    "frames": 121  # 121=5秒, 241=10秒
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

5. 从输出获取 task_id，轮询：

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "jimeng_i2v_first_v30" --task-id "TASK_ID" --max-wait 300 --interval 5
```

6. 下载视频并发送给用户：

```bash
python3 {baseDir}/scripts/jimeng_helper.py download --url "视频URL" --dir "~/jimeng-videos" --prefix "jimeng_i2v" --ext "mp4"
```

### 4. 图片编辑 Inpainting

**需要用户图片。按「用户文件获取流程」获取图片的本地路径。**

1. 获取图片本地路径
2. 获取用户编辑描述（如"把背景换成海边"）
3. **用 inline Python 提交**：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("此处替换为图片的完整本地路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_image2image_dream_inpaint",
    "prompt": "此处替换为编辑描述",
    "binary_data_base64": [image_b64]  # 注意：用 binary_data_base64
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

4. 轮询时需附加 req_json：

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
    "task_id": "此处替换为task_id",
    "req_json": "{\"return_url\":true,\"logo_info\":{\"add_logo\":false}}"
}
resp = vs.cv_sync2async_get_result(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

重复查询直到 `data.image_urls` 出现或失败（间隔 3 秒，最多等 180 秒）。

5. 下载到 `~/jimeng-images/`，prefix=`jimeng_edit`，ext=`png`

### 5. 智能超清

**需要用户图片。按「用户文件获取流程」获取图片的本地路径。**

1. 获取图片本地路径
2. **用 inline Python 提交**：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("此处替换为图片的完整本地路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_high_aes_general_v21_L",
    "binary_data_base64": [image_b64]  # 注意：用 binary_data_base64
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

3. 轮询结果（interval=3, max_wait=180）→ 下载到 `~/jimeng-images/`，prefix=`jimeng_hd`，ext=`png`

### 6. 数字人（两步）

**需要用户图片和音频。按「用户文件获取流程」分别获取两个文件。**

图片要求：JPG/PNG, <5MB, **必须单人正面清晰**
音频要求：时长 < 15秒

1. 获取图片和音频的本地路径
2. **步骤1 主体识别**（同步）：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("此处替换为图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")

form = {
    "req_key": "jimeng_realman_avatar_picture_create_role_omni",
    "image_base64": image_b64
}
resp = vs.cv_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

确认 code=10000 且 status=1。失败则提示换正面清晰人物图。

3. **步骤2 视频生成**：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("此处替换为图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")
with open("此处替换为音频路径", "rb") as f:
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

4. 轮询（interval=5, max_wait=300）→ 下载到 `~/jimeng-videos/`，prefix=`jimeng_dh`，ext=`mp4`

### 7. 动作模仿 2.0

**需要用户图片和视频。按「用户文件获取流程」分别获取两个文件。**

图片要求：JPEG/PNG, 480x480~1920x1080, < 4.7MB
视频要求：MP4/MOV/WebM, ≤ 30秒

1. 获取图片和视频的本地路径
2. **用 inline Python 提交**：

```bash
python3 << 'PYEOF'
import json, os, base64
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)
vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])

with open("此处替换为图片路径", "rb") as f:
    image_b64 = base64.b64encode(f.read()).decode("utf-8")
with open("此处替换为视频路径", "rb") as f:
    video_b64 = base64.b64encode(f.read()).decode("utf-8")

# 动作模仿：图片用 image_base64（字符串），视频用 binary_data_base64（数组）
form = {
    "req_key": "jimeng_motion_imitation_v2",
    "image_base64": image_b64,
    "binary_data_base64": [video_b64]  # 注意：视频用 binary_data_base64，不是 video_base64！
}
resp = vs.cv_sync2async_submit_task(form)
print(json.dumps(resp, ensure_ascii=False, indent=2))
PYEOF
```

3. 轮询（max_wait=600, interval=5，处理较慢约 3 分钟+）→ 下载到 `~/jimeng-videos/`，prefix=`jimeng_motion`，ext=`mp4`

---

## 错误处理

| 场景 | 处理 |
|------|------|
| 未配置密钥 | 引导配置 ~/.jimeng/config.json |
| API 认证失败 | 提示检查 AK/SK |
| 50218 安全检查 | 提示换正面清晰无遮挡图片 |
| 余额不足 | 提示充值火山引擎 |
| 超时 | 提供 task_id 供手动查询 |
| 下载失败 | 提供 URL 供手动下载 |
| 找不到用户文件 | 搜索 ~/.openclaw/media/inbound/ 或要求用户重新发送 |
| 飞书发送失败 | 告知用户本地文件路径，让用户手动获取 |

## 详细 API 参考

见 [api-reference.md](references/api-reference.md)
