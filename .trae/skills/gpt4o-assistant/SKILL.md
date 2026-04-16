---
name: "gpt4o-assistant"
description: "Calls GPT-4o model via specified API endpoint. Invoke when user needs AI assistance, text generation, or code analysis using the configured GPT-4o API."
---

# GPT-4o Assistant

This skill provides access to the GPT-4o model through a custom API endpoint. It uses the following configuration:

## API Configuration
- **API Endpoint**: `https://api.apiyi.com/v1`
- **API Key**: 964c79f34bdf431996587309d17ac072
- **Model**: gpt-4o

## Usage

When this skill is invoked, it will:
1. Send a request to the configured API endpoint
2. Use the provided API key for authentication
3. Process the user's query using the GPT-4o model
4. Return the AI-generated response

## How to Use

The skill can be invoked in several ways:

1. **Direct invocation**: When the user explicitly asks for AI assistance or mentions using GPT-4o
2. **Automatic invocation**: When the task requires creative writing, code generation, problem solving, or text analysis
3. **Contextual invocation**: When the conversation involves complex reasoning or knowledge-intensive tasks

## Technical Details

The skill uses the OpenAI-compatible API interface. The request format is:

```json
{
  "model": "gpt-4o",
  "messages": [
    {"role": "user", "content": "User's query here"}
  ],
  "temperature": 0.7,
  "max_tokens": 2000
}
```

## Security Notes

- The API key is embedded in the skill configuration
- All API calls are made over HTTPS
- The skill only uses the configured endpoint and model

## Examples

**User**: "帮我写一个Python函数来计算斐波那契数列"
**Skill Action**: Invoke GPT-4o to generate the Python code with explanation

**User**: "解释一下量子计算的基本原理"
**Skill Action**: Invoke GPT-4o to provide a detailed explanation

**User**: "帮我分析这段代码的性能问题"
**Skill Action**: Invoke GPT-4o to review and analyze the code