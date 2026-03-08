---
name: jimeng-ai
description: 即梦 AI 多模态生成。当用户提到"生成视频"、"生成图片"、"文生视频"、"文生图"、"图生视频"、"即梦"、"jimeng"、"AI视频"、"AI图片"、"数字人"、"动作模仿"、"图片超清"、"图片编辑"、"inpainting"、"超分辨率"、"画一张"、"做个视频"、"口播"时使用。通过火山引擎即梦 AI API 生成图片和视频。
version: 2.0.0
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
| 图片转视频 | 图生视频 | 图片 + prompt |
| 编辑修改图片 | Inpainting | 图片 + prompt |
| 图片放大增强 | 智能超清 | 图片 |
| 图片+音频做口播 | 数字人 | 图片 + 音频 |
| 图片+视频做动作迁移 | 动作模仿 | 图片 + 视频 |

## 通用流程

### 处理飞书发来的文件

用户通过飞书对话发送图片/音频/视频时：

1. 识别文件来源（本地路径或 URL）
2. 如果是 URL，下载到本地：
```bash
python3 {baseDir}/scripts/jimeng_helper.py save-url --url "FILE_URL" --ext jpg
```
3. 转为 base64 传入 API：
```bash
python3 {baseDir}/scripts/jimeng_helper.py base64 --file "LOCAL_PATH"
```

### 提交任务

```bash
python3 {baseDir}/scripts/jimeng_helper.py submit --form '{"req_key":"...","prompt":"..."}'
```

### 轮询结果

```bash
python3 {baseDir}/scripts/jimeng_helper.py poll --req-key "REQ_KEY" --task-id "TASK_ID" --max-wait 300
```

### 下载文件

```bash
python3 {baseDir}/scripts/jimeng_helper.py download --url "FILE_URL" --dir "~/jimeng-videos" --prefix "jimeng" --ext "mp4"
```

## 各功能详细流程

### 1. 文生图 4.0

1. 获取用户描述
2. **AI 优化提示词**：补充画面细节、构图、光影、色彩、风格，不超过 300 字。展示给用户确认
3. 提交任务：`{"req_key": "jimeng_t2i_v40", "prompt": "优化后提示词", "seed": -1}`
4. 轮询结果（interval=3, max_wait=180）
5. 从 `data.image_urls` 下载图片到 `~/jimeng-images/`，prefix=`jimeng`，ext=`png`
6. 告知用户文件路径和大小

### 2. 文生视频 3.0 Pro

1. 获取用户描述
2. **AI 优化提示词**：补充运动描述、镜头语言、氛围，不超过 400 字。展示给用户确认
3. 询问参数：分辨率(720p/1080p)、时长(5秒/10秒)、比例(16:9/9:16/1:1/4:3/3:4/21:9)
4. 确定 req_key：720p→`jimeng_t2v_v30`，1080p→`jimeng_t2v_v30_1080p`
5. 提交：`{"req_key":"...","prompt":"...","seed":-1,"frames":121或241,"aspect_ratio":"..."}`
6. 轮询结果（interval=5, max_wait=300）
7. 从结果下载视频到 `~/jimeng-videos/`，prefix=`jimeng`，ext=`mp4`

### 3. 图生视频

1. 获取用户发送的图片→保存本地→base64
2. 获取描述→AI 优化提示词→用户确认
3. 询问：分辨率(720p/1080p)、时长(5s/10s)、是否运镜(仅720p)
4. 提交：`{"req_key":"jimeng_i2v_first_v30","prompt":"...","image_base64":["BASE64"],"seed":-1,"frames":121}`
5. 轮询→下载到 `~/jimeng-videos/`，prefix=`jimeng_i2v`

运镜模式用 `jimeng_i2v_recamera_v30`，加 `template_id` 和 `camera_strength`。

### 4. 图片编辑 Inpainting

1. 获取用户发送的图片→保存本地→base64
2. 获取编辑描述（如"把背景换成海边"）
3. 提交：`{"req_key":"jimeng_image2image_dream_inpaint","prompt":"...","image_base64":["BASE64"]}`
4. 轮询时查询 form 附加 `"req_json":"{\"return_url\":true,\"logo_info\":{\"add_logo\":false}}"`
5. 从 `data.image_urls` 下载到 `~/jimeng-images/`，prefix=`jimeng_edit`

### 5. 智能超清

1. 获取用户发送的图片→保存本地→base64
2. 提交：`{"req_key":"jimeng_high_aes_general_v21_L","image_base64":["BASE64"]}`
3. 轮询→从 `data.image_urls` 下载到 `~/jimeng-images/`，prefix=`jimeng_hd`

### 6. 数字人（两步）

1. 获取用户发送的人物图片→保存本地→base64
2. 获取音频（用户发送的音频文件，同样保存本地→base64）
3. **步骤1 主体识别**（同步）：
   ```bash
   python3 {baseDir}/scripts/jimeng_helper.py submit-sync --form '{"req_key":"jimeng_realman_avatar_picture_create_role_omni","image_base64":"BASE64"}'
   ```
   确认 code=10000 且 status=1。失败则提示换正面清晰人物图
4. **步骤2 视频生成**：
   提交：`{"req_key":"jimeng_realman_avatar_picture_omni_v2","image_base64":"BASE64","audio_base64":"BASE64"}`
5. 轮询→下载到 `~/jimeng-videos/`，prefix=`jimeng_dh`
6. 图片要求：JPG/PNG, <5MB, 单人正面。音频要求：<15秒。输出：480P MP4

### 7. 动作模仿 2.0

1. 获取用户发送的人物图片→保存本地→base64
2. 获取用户发送的模板视频→保存本地→base64
3. 提交：`{"req_key":"jimeng_motion_imitation_v2","image_base64":"BASE64","video_base64":"BASE64"}`
4. 轮询（max_wait=600, interval=5，处理较慢）
5. 下载到 `~/jimeng-videos/`，prefix=`jimeng_motion`
6. 图片要求：JPEG/PNG, 480x480~1920x1080, <4.7MB。视频要求：MP4/MOV/WebM, ≤30秒

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

## 详细 API 参考

见 [api-reference.md](references/api-reference.md)
