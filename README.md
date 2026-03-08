# 即梦 AI 多模态生成 - Claude Code 插件

通过火山引擎即梦 AI API，在 Claude Code 中直接生成图片和视频。支持 AI 提示词优化，覆盖即梦全线模型。

## 支持的功能

| 功能 | 命令 | 说明 |
|------|------|------|
| 文生图 4.0 | `/jimeng-image` | 文字描述生成高质量图片 |
| 文生视频 3.0 Pro | `/jimeng-video` | 文字描述生成视频，720p/1080p |
| 图生视频 3.0 Pro | `/jimeng-i2v` | 图片转视频，支持运镜 |
| 交互编辑 Inpainting | `/jimeng-inpaint` | 局部编辑修改图片 |
| 智能超清 | `/jimeng-upscale` | 图片放大增强 |
| 数字人快速模式 | `/jimeng-digital-human` | 图片+音频生成口播视频 |
| 动作模仿 2.0 | `/jimeng-motion` | 图片+视频动作迁移 |
| 配置密钥 | `/jimeng-setup` | 配置火山引擎 AK/SK |

所有功能也支持自然语言触发（如"帮我生成一张图片"、"把这张图做成视频"）。

## 安装

```bash
claude plugin add https://github.com/wyzz973/jimeng-skills.git
```

## 使用

### 1. 配置密钥

```
/jimeng-setup
```

> 获取密钥：[火山引擎控制台](https://console.volcengine.com) → 右上角账户 → API 访问密钥
> 开通服务：[智能视觉控制台](https://console.volcengine.com/ai/overview) 开通所需的即梦 AI 服务

### 2. 文生图

```
/jimeng-image 一只猫坐在窗台上看夕阳
```

### 3. 文生视频

```
/jimeng-video 千军万马奔腾而来
```

### 4. 图生视频

```
/jimeng-i2v https://example.com/photo.jpg 让画面动起来
```

### 5. 图片编辑

```
/jimeng-inpaint https://example.com/photo.jpg 把背景换成海边
```

### 6. 智能超清

```
/jimeng-upscale https://example.com/low-res.jpg
```

### 7. 数字人

```
/jimeng-digital-human https://example.com/person.jpg https://example.com/audio.mp3
```

### 8. 动作模仿

```
/jimeng-motion https://example.com/person.jpg https://example.com/dance.mp4
```

## 输出目录

- 图片保存到：`~/jimeng-images/`
- 视频保存到：`~/jimeng-videos/`

## 前置条件

- 火山引擎账号，并开通对应的[即梦 AI 服务](https://console.volcengine.com/ai/overview)
- Python 3.x
- `volcengine` SDK（插件会自动安装）

## 文件结构

```
jimeng-skills/
├── .claude-plugin/
│   └── plugin.json
├── commands/
│   ├── jimeng-setup.md           # 配置密钥
│   ├── jimeng-image.md           # 文生图 4.0
│   ├── jimeng-video.md           # 文生视频 3.0 Pro
│   ├── jimeng-i2v.md             # 图生视频
│   ├── jimeng-inpaint.md         # 交互编辑
│   ├── jimeng-upscale.md         # 智能超清
│   ├── jimeng-digital-human.md   # 数字人
│   └── jimeng-motion.md          # 动作模仿 2.0
└── skills/
    └── jimeng-video/
        └── SKILL.md              # 自动触发 skill
```

## API 参考

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

## License

MIT
