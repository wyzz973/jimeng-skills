# 即梦 AI 文生视频 - Claude Code 插件

通过火山引擎即梦 AI API，在 Claude Code 中直接生成视频。支持 AI 提示词优化、多分辨率、多时长选择。

## 功能

- **AI 提示词优化** - 大模型自动优化你的视频描述，补充画面细节、运动、光影、风格等
- **多分辨率** - 支持 720p / 1080p
- **多时长** - 5 秒 / 10 秒
- **多比例** - 16:9、9:16、1:1、4:3、3:4、21:9
- **自动触发** - 说"帮我生成视频"即可，无需记忆命令

## 安装

```bash
claude plugin add https://github.com/wyzz973/jimeng-skills.git
```

## 使用

### 1. 配置密钥

首次使用前，运行：

```
/jimeng-setup
```

按提示输入火山引擎的 Access Key 和 Secret Key。

> 获取密钥：[火山引擎控制台](https://console.volcengine.com) → 右上角账户 → API 访问密钥

### 2. 生成视频

**方式一：命令调用**

```
/jimeng-video 一只猫在月光下散步
```

**方式二：自然语言（自动触发）**

```
帮我生成一个视频：千军万马奔腾而来
```

### 3. 生成流程

1. 输入视频描述
2. AI 优化提示词 → 确认或修改
3. 选择分辨率、时长、画面比例
4. 等待生成（约 1-3 分钟）
5. 视频自动下载到 `~/jimeng-videos/`

## 前置条件

- 火山引擎账号，并开通[即梦 AI 视频生成服务](https://console.volcengine.com/ai/overview)
- Python 3.x
- `volcengine` SDK（插件会自动安装）

## 文件结构

```
jimeng-skills/
├── .claude-plugin/
│   └── plugin.json            # 插件元数据
├── commands/
│   ├── jimeng-setup.md        # /jimeng-setup 配置命令
│   └── jimeng-video.md        # /jimeng-video 生成命令
└── skills/
    └── jimeng-video/
        └── SKILL.md           # 自动触发 skill
```

## API 参考

| 参数 | 可选值 |
|------|--------|
| req_key (720p) | `jimeng_t2v_v30` |
| req_key (1080p) | `jimeng_t2v_v30_1080p` |
| frames (5秒) | `121` |
| frames (10秒) | `241` |
| aspect_ratio | `16:9` `4:3` `1:1` `3:4` `9:16` `21:9` |

## License

MIT
