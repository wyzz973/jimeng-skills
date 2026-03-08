---
name: jimeng-ai
description: 当用户提到"生成视频"、"生成图片"、"文生视频"、"文生图"、"图生视频"、"即梦"、"jimeng"、"AI视频"、"AI图片"、"视频生成"、"图片生成"、"数字人"、"动作模仿"、"图片超清"、"图片编辑"、"inpainting"、"超分辨率"等与即梦 AI 生成相关的请求时，自动触发此 skill。
version: 2.0.0
---

# 即梦 AI 多模态生成 Skill

当检测到用户有图片/视频生成需求时，自动执行以下流程。

## 前置条件检查

1. **检查配置文件** `~/.jimeng/config.json` 是否存在
   - 如果不存在，引导用户使用 `/jimeng-setup` 命令配置 Access Key 和 Secret Key
   - 如果存在，读取其中的 `access_key` 和 `secret_key`

2. **检查 Python 依赖**
   ```bash
   pip install volcengine requests -q 2>/dev/null
   ```

## 功能识别

根据用户意图判断调用哪个功能：

| 用户意图 | 功能 | 命令 |
|---------|------|------|
| 文字描述生成图片 | 文生图 4.0 | `/jimeng-image` |
| 文字描述生成视频 | 文生视频 3.0 Pro | `/jimeng-video` |
| 上传图片生成视频 | 图生视频 3.0 Pro | `/jimeng-i2v` |
| 编辑/修改图片局部 | 交互编辑 inpainting | `/jimeng-inpaint` |
| 图片放大/增强清晰度 | 智能超清 | `/jimeng-upscale` |
| 图片+音频生成数字人 | 数字人快速模式 | `/jimeng-digital-human` |
| 图片+视频动作模仿 | 动作模仿 2.0 | `/jimeng-motion` |

---

## 一、文生图 4.0

### 触发词
"生成图片"、"画一张"、"文生图"、"AI 画图"

### 流程
1. 获取用户描述 → AI 优化提示词（补充画面细节、风格、光影、构图，不超过 300 字）
2. 用户确认提示词
3. 询问图片参数（比例、数量）
4. 提交任务 → 轮询结果 → 下载图片

### API 参数
```python
form = {
    "req_key": "jimeng_t2i_v40",
    "prompt": "优化后的提示词",
    "seed": -1,
    "scale": 0.5  # 可选，控制参数
}
resp = vs.cv_sync2async_submit_task(form)
```

### 查询结果
```python
form = {"req_key": "jimeng_t2i_v40", "task_id": task_id}
resp = vs.cv_sync2async_get_result(form)
# 成功时: resp["data"]["image_urls"] 包含图片URL列表
```

### 下载保存
保存到 `~/jimeng-images/jimeng_YYYYMMDD_HHMMSS.png`

---

## 二、文生视频 3.0 Pro

### 触发词
"生成视频"、"文生视频"、"做一个视频"

### 流程
1. 获取用户描述 → AI 优化提示词（补充运动、镜头、氛围，不超过 400 字）
2. 用户确认提示词
3. 询问：分辨率(720p/1080p)、时长(5s/10s)、画面比例
4. 提交任务 → 轮询结果 → 下载视频

### API 参数
```python
form = {
    "req_key": "jimeng_t2v_v30",       # 720p
    # "req_key": "jimeng_t2v_v30_1080p", # 1080p
    "prompt": "优化后的提示词",
    "seed": -1,
    "frames": 121,        # 121=5秒, 241=10秒
    "aspect_ratio": "16:9"  # 16:9/4:3/1:1/3:4/9:16/21:9
}
resp = vs.cv_sync2async_submit_task(form)
```

### 查询与下载
```python
form = {"req_key": req_key, "task_id": task_id}
resp = vs.cv_sync2async_get_result(form)
# 成功时: resp["data"] 中包含 video_url
```
保存到 `~/jimeng-videos/jimeng_YYYYMMDD_HHMMSS.mp4`

---

## 三、图生视频 3.0 Pro

### 触发词
"图片转视频"、"图生视频"、"这张图做成视频"

### 流程
1. 获取用户上传的图片（需要图片 URL，可让用户提供 URL 或本地路径后上传）
2. 获取用户描述 → AI 优化提示词
3. 询问：分辨率(720p/1080p)、时长(5s/10s)
4. 提交任务 → 轮询结果 → 下载视频

### API 参数

**首帧图生视频：**
```python
form = {
    "req_key": "jimeng_i2v_first_v30",        # 720p
    # "req_key": "jimeng_i2v_first_v30_1080",  # 1080p
    "prompt": "优化后的提示词",
    "image_urls": ["https://图片URL"],
    "seed": -1,
    "frames": 121  # 121=5秒, 241=10秒
}
resp = vs.cv_sync2async_submit_task(form)
```

**720p 运镜模式（可选）：**
```python
form = {
    "req_key": "jimeng_i2v_recamera_v30",
    "prompt": "提示词",
    "image_urls": ["https://图片URL"],
    "template_id": "hitchcock_dolly_in",  # 运镜模板
    "camera_strength": "medium"  # weak/medium/strong
}
```

---

## 四、交互编辑 Inpainting

### 触发词
"编辑图片"、"修改图片"、"inpainting"、"图片局部修改"

### 流程
1. 获取用户上传的原图 URL
2. 获取用户的编辑需求描述
3. 提交任务 → 查询结果 → 下载编辑后的图片

### API 参数
```python
# 提交编辑任务
form = {
    "req_key": "jimeng_image2image_dream_inpaint",
    "prompt": "编辑描述，如：背景换成演唱会现场",
    "image_urls": ["https://原图URL"]
}
resp = vs.cv_sync2async_submit_task(form)

# 查询结果
form = {
    "req_key": "jimeng_image2image_dream_inpaint",
    "task_id": task_id,
    "req_json": "{\"return_url\":true,\"logo_info\":{\"add_logo\":false}}"
}
resp = vs.cv_sync2async_get_result(form)
# 成功时: resp["data"]["image_urls"] 包含编辑后的图片URL
```

### 下载保存
保存到 `~/jimeng-images/jimeng_edit_YYYYMMDD_HHMMSS.png`

---

## 五、智能超清

### 触发词
"图片超清"、"图片放大"、"超分辨率"、"提升画质"、"图片增强"

### 流程
1. 获取用户上传的图片 URL
2. 提交超清任务 → 轮询结果 → 下载增强后的图片

### API 参数
```python
form = {
    "req_key": "jimeng_high_aes_general_v21_L",
    "image_urls": ["https://原图URL"]
}
resp = vs.cv_sync2async_submit_task(form)

# 查询结果
form = {"req_key": "jimeng_high_aes_general_v21_L", "task_id": task_id}
resp = vs.cv_sync2async_get_result(form)
# 成功时: resp["data"]["image_urls"] 包含超清图片URL
```

### 下载保存
保存到 `~/jimeng-images/jimeng_hd_YYYYMMDD_HHMMSS.png`

---

## 六、数字人快速模式 (OmniHuman)

### 触发词
"数字人"、"口播视频"、"人物说话"、"音频驱动"

### 流程（两步调用）

**步骤1：主体识别**
```python
form = {
    "req_key": "jimeng_realman_avatar_picture_create_role_omni",
    "image_url": "https://人物图片URL"
}
resp = vs.cv_submit_task(form)
# 查询识别结果，确认 status=1（识别到有效主体）
```

**步骤2：视频生成**
```python
form = {
    "req_key": "jimeng_realman_avatar_picture_omni_v2",
    "image_url": "https://人物图片URL",
    "audio_url": "https://音频URL"
}
resp = vs.cv_sync2async_submit_task(form)
# 查询结果中 video_url 即为生成的数字人视频
```

### 输入要求
- 图片：JPG/PNG，< 5MB，分辨率 < 4096x4096，建议单人正面
- 音频：建议 < 15秒
- 输出：480P MP4 视频

### 下载保存
保存到 `~/jimeng-videos/jimeng_dh_YYYYMMDD_HHMMSS.mp4`

---

## 七、动作模仿 2.0

### 触发词
"动作模仿"、"动作迁移"、"模仿动作"、"跟着动"

### 流程
1. 获取用户上传的人物图片 URL
2. 获取模板视频 URL（用户上传或从预设中选择）
3. 提交任务 → 轮询结果 → 下载视频

### API 参数
```python
form = {
    "req_key": "jimeng_motion_imitation_v2",
    "image_url": "https://人物图片URL",
    "video_url": "https://模板视频URL"
}
resp = vs.cv_sync2async_submit_task(form)
# 查询结果中 video_url 即为生成的模仿视频
```

### 输入要求
- 图片：JPEG/PNG，480x480 ~ 1920x1080，< 4.7MB
- 视频：MP4/MOV/WebM，≤ 30秒，200x200 ~ 2048x1440
- 输出：720P 25fps MP4

### 下载保存
保存到 `~/jimeng-videos/jimeng_motion_YYYYMMDD_HHMMSS.mp4`

---

## 通用 SDK 调用模板

所有功能共用以下初始化代码：

```python
import json, os, time, requests
from volcengine.visual.VisualService import VisualService

with open(os.path.expanduser("~/.jimeng/config.json")) as f:
    config = json.load(f)

vs = VisualService()
vs.set_ak(config["access_key"])
vs.set_sk(config["secret_key"])
```

### 通用轮询逻辑
```python
max_attempts = 60
interval = 5
for i in range(max_attempts):
    form = {"req_key": req_key, "task_id": task_id}
    resp = vs.cv_sync2async_get_result(form)
    data = resp.get("data", {})
    if data.get("status") == "done" or data.get("image_urls") or data.get("video_url"):
        break  # 任务完成
    if "fail" in str(data.get("status", "")).lower():
        break  # 任务失败
    time.sleep(interval)
```

### 通用下载逻辑
```python
def download_file(url, save_dir, prefix, ext):
    os.makedirs(os.path.expanduser(save_dir), exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{timestamp}.{ext}"
    filepath = os.path.join(os.path.expanduser(save_dir), filename)
    r = requests.get(url, stream=True)
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    return filepath
```

## 错误处理

| 场景 | 处理方式 |
|------|---------|
| 未配置密钥 | 引导使用 `/jimeng-setup` |
| API 认证失败 | 提示检查 AK/SK 是否正确 |
| 余额不足 | 提示充值火山引擎账户 |
| 参数错误 | 解析错误信息并修正 |
| 生成超时 | 提供 task_id 供手动查询 |
| 下载失败 | 提供文件 URL 供手动下载 |
| 图片/音频/视频 URL 无效 | 提示用户重新提供有效 URL |
