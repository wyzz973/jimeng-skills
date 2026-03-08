---
description: 配置即梦 AI 的 Access Key 和 Secret Key
allowed-tools: [Bash, Read, Write, AskUserQuestion]
---

# 即梦 AI 配置向导

帮助用户配置火山引擎即梦 AI 的 API 凭证。

## 步骤

### 1. 检查现有配置

首先检查是否已有配置文件：

```bash
cat ~/.jimeng/config.json 2>/dev/null
```

如果已存在配置，告知用户当前已配置（隐藏 SK 的大部分字符），并询问是否要更新。

### 2. 引导用户获取密钥

如果没有配置或用户要更新，告知用户：

> 要使用即梦 AI 文生视频功能，需要火山引擎的 Access Key (AK) 和 Secret Access Key (SK)。
>
> **获取方式：**
> 1. 登录 [火山引擎控制台](https://console.volcengine.com)
> 2. 点击右上角账户 → "API 访问密钥"
> 3. 创建或复制已有的 AK/SK
> 4. 前往 [智能视觉控制台](https://console.volcengine.com/ai/overview) 开通"即梦 AI-视频生成"服务

然后使用 AskUserQuestion 分别询问用户的 Access Key 和 Secret Key。

### 3. 保存配置

将凭证保存到 `~/.jimeng/config.json`：

```bash
mkdir -p ~/.jimeng
```

写入以下格式的 JSON（使用用户提供的实际值）：

```json
{
  "access_key": "用户提供的AK",
  "secret_key": "用户提供的SK"
}
```

设置文件权限为仅用户可读：

```bash
chmod 600 ~/.jimeng/config.json
```

### 4. 验证配置

尝试使用配置进行一次简单的 API 调用来验证凭证是否有效：

```bash
pip install volcengine -q 2>/dev/null
python3 -c "
from volcengine.visual.VisualService import VisualService
import json

with open('$HOME/.jimeng/config.json') as f:
    config = json.load(f)

vs = VisualService()
vs.set_ak(config['access_key'])
vs.set_sk(config['secret_key'])
print('凭证格式正确，配置已保存！')
"
```

告知用户配置完成，可以使用 `/jimeng-video` 命令或直接说"帮我生成一个视频"来开始使用。
