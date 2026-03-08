# 即梦 AI 多模态生成 - OpenClaw Skill

通过火山引擎即梦 AI API 生成图片和视频。支持 AI 提示词优化，覆盖即梦全线 7 大功能。

## 支持的功能

| 功能 | 说明 |
|------|------|
| 文生图 4.0 | 文字描述生成高质量图片 |
| 文生视频 3.0 Pro | 文字描述生成视频，720p/1080p |
| 图生视频 3.0 Pro | 图片转视频，支持运镜 |
| 交互编辑 Inpainting | 局部编辑修改图片 |
| 智能超清 | 图片放大增强 |
| 数字人快速模式 | 图片+音频生成口播视频 |
| 动作模仿 2.0 | 图片+视频动作迁移 |

所有功能支持自然语言触发（如"帮我生成一张图片"、"把这张图做成视频"、"图片超清"等）。

## 安装

将整个目录复制到 OpenClaw skills 目录：

```bash
git clone https://github.com/wyzz973/jimeng-skills.git
cp -r jimeng-skills ~/.openclaw/skills/jimeng-ai
```

或手动下载 zip 包解压到 `~/.openclaw/skills/jimeng-ai/`。

## 首次使用

1. 获取密钥：[火山引擎控制台](https://console.volcengine.com) → 右上角账户 → API 访问密钥
2. 开通服务：[智能视觉控制台](https://console.volcengine.com/ai/overview) 开通所需的即梦 AI 服务
3. 在对话中告诉 AI 你的 Access Key 和 Secret Key，会自动保存配置
4. 安装 Python 依赖：`pip install volcengine requests`

## 使用示例

在飞书 OpenClaw 对话中直接说：

- "帮我画一只猫坐在窗台上看夕阳"
- "生成一个千军万马奔腾的视频"
- "把这张图片做成视频"（发送图片后）
- "帮我把这张图片变清晰"（发送图片后）
- "用这张人物图和这段音频做一个口播视频"

## 输出目录

- 图片保存到：`~/jimeng-images/`
- 视频保存到：`~/jimeng-videos/`

## 前置条件

- 火山引擎账号，并开通对应的[即梦 AI 服务](https://console.volcengine.com/ai/overview)
- Python 3.x
- `volcengine` 和 `requests` Python 包

## 文件结构

```
jimeng-ai/
├── SKILL.md                    # OpenClaw Skill 主文件
├── scripts/
│   └── jimeng_helper.py        # 通用辅助脚本
├── references/
│   └── api-reference.md        # API 参考文档
└── README.md
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
