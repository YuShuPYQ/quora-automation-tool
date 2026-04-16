# Trae 自定义模型配置

## GPT-4o (apiyi.com) 配置

已成功配置自定义GPT-4o模型到Trae软件中。

### 模型信息
- **模型ID**: `gpt-4o-apiyi`
- **显示名称**: GPT-4o (apiyi.com)
- **API端点**: `https://api.apiyi.com/v1`
- **API密钥**: 964c79f34bdf431996587309d17ac072
- **模型名称**: gpt-4o

### 配置文件
1. **模型配置**: `.trae/models.json` - 包含自定义模型定义
2. **技能配置**: `.trae/skills/gpt4o-assistant/SKILL.md` - 包含技能调用逻辑

### 使用方法

#### 方法1: 作为自定义模型使用
在Trae软件的模型选择中，应该可以看到 "GPT-4o (apiyi.com)" 选项。

#### 方法2: 通过技能调用
在对话中直接请求GPT-4o帮助：
- "请使用GPT-4o帮我分析这段代码"
- "调用GPT-4o技能处理这个问题"
- "我需要GPT-4o的AI协助"

#### 方法3: 自动触发
当对话涉及以下内容时，系统会自动推荐或使用GPT-4o：
- 代码生成和分析
- 复杂问题解决
- 文本创作和翻译
- 知识密集型任务

### API配置详情
```json
{
  "base_url": "https://api.apiyi.com/v1",
  "api_key": "964c79f34bdf431996587309d17ac072",
  "model": "gpt-4o",
  "temperature": 0.7,
  "max_tokens": 2000
}
```

### 注意事项
1. API端点可能需要完整的路径（如 `/v1/chat/completions`）
2. 确保API密钥有效且未过期
3. 模型响应时间取决于API服务状态

### 验证方法
尝试在Trae对话框中输入：
```
请使用GPT-4o自定义模型帮我写一个简单的Python程序
```

如果配置成功，您将收到来自GPT-4o模型的响应。