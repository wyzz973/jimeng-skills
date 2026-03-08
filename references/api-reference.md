# 即梦 AI API 参考

## req_key 一览

| 功能 | req_key |
|------|---------|
| 文生图 4.0 | `jimeng_t2i_v40` |
| 文生视频 720p | `jimeng_t2v_v30` |
| 文生视频 1080p | `jimeng_t2v_v30_1080p` |
| 图生视频首帧 720p | `jimeng_i2v_first_v30` |
| 图生视频首帧 1080p | `jimeng_i2v_first_v30_1080` |
| 图生视频运镜 720p | `jimeng_i2v_recamera_v30` |
| 交互编辑 Inpainting | `jimeng_image2image_dream_inpaint` |
| 智能超清 | `jimeng_high_aes_general_v21_L` |
| 数字人主体识别 | `jimeng_realman_avatar_picture_create_role_omni` |
| 数字人视频生成 | `jimeng_realman_avatar_picture_omni_v2` |
| 动作模仿 2.0 | `jimeng_motion_imitation_v2` |

## 文生图 4.0

```json
{"req_key": "jimeng_t2i_v40", "prompt": "描述文本", "seed": -1}
```

结果字段：`data.image_urls`

## 文生视频 3.0 Pro

```json
{
  "req_key": "jimeng_t2v_v30",
  "prompt": "描述文本",
  "seed": -1,
  "frames": 121,
  "aspect_ratio": "16:9"
}
```

- frames: `121`=5秒, `241`=10秒
- aspect_ratio: `16:9` `4:3` `1:1` `3:4` `9:16` `21:9`
- 1080p 改 req_key 为 `jimeng_t2v_v30_1080p`
- 结果字段：`data.video_url`

## 图生视频

```json
{
  "req_key": "jimeng_i2v_first_v30",
  "prompt": "描述",
  "image_base64": ["BASE64_STRING"],
  "seed": -1,
  "frames": 121
}
```

运镜模式额外参数：
- `template_id`: 如 `hitchcock_dolly_in`
- `camera_strength`: `weak` / `medium` / `strong`

## 交互编辑 Inpainting

提交：
```json
{"req_key": "jimeng_image2image_dream_inpaint", "prompt": "编辑描述", "image_base64": ["BASE64"]}
```

查询时附加：
```json
{"req_json": "{\"return_url\":true,\"logo_info\":{\"add_logo\":false}}"}
```

结果字段：`data.image_urls`

## 智能超清

```json
{"req_key": "jimeng_high_aes_general_v21_L", "image_base64": ["BASE64"]}
```

结果字段：`data.image_urls`

## 数字人（两步）

步骤1 主体识别（同步）：
```json
{"req_key": "jimeng_realman_avatar_picture_create_role_omni", "image_base64": "BASE64"}
```
确认 code=10000 且 status=1

步骤2 视频生成：
```json
{"req_key": "jimeng_realman_avatar_picture_omni_v2", "image_base64": "BASE64", "audio_base64": "BASE64"}
```

- 图片：JPG/PNG, <5MB, 建议单人正面
- 音频：<15秒
- 输出：480P MP4

## 动作模仿 2.0

```json
{"req_key": "jimeng_motion_imitation_v2", "image_base64": "BASE64", "video_base64": "BASE64"}
```

- 图片：JPEG/PNG, 480x480~1920x1080, <4.7MB
- 视频：MP4/MOV/WebM, ≤30秒
- 输出：720P 25fps MP4, RTF~18

## 通用说明

- base64 方式传文件：用 `image_base64` / `audio_base64` / `video_base64` 替代对应的 `_url` / `_urls` 参数
- 提交接口：`cv_sync2async_submit_task(form)` 返回 `task_id`
- 查询接口：`cv_sync2async_get_result(form)` 返回结果
- 同步接口（仅主体识别）：`cv_submit_task(form)`
