# Quora 自动化发帖流程优化与实现计划

## 目标
实现一个自动化脚本，能够自动识别当前已打开并处于调试模式的 Google Chrome 浏览器实例，并连接该实例执行 Quora 发帖任务。

## 核心痛点解决
正如您提供的分析所言，普通启动的 Chrome 浏览器无法被程序直接接管。
**解决方案**：必须以“调试模式”启动浏览器，指定 `--remote-debugging-port`。

## 实施步骤

### 1. 浏览器启动配置 (手动/半自动)
- 创建一个批处理脚本 (`start_chrome.bat`)，用于快捷启动带有特定调试端口 (如 9222, 9223) 和独立用户数据目录的 Chrome 浏览器。
- 用户需使用此脚本打开浏览器，进行手动登录和注册 Quora。

### 2. 编写自动识别与控制脚本 (Python)
我们将使用 Python 和 `playwright` (或 `selenium`) 来实现：
- **端口扫描**: 脚本将循环检测本地端口 (如 9222-9230)，寻找活跃的 Chrome 调试接口。
- **状态判断**: 通过访问 `http://127.0.0.1:{port}/json/version` 来确认浏览器是否打开且可连接。
- **自动连接**: 一旦发现活跃端口，立即通过 CDP (Chrome DevTools Protocol) 连接该浏览器实例。
- **任务执行**: 连接后，脚本将控制该浏览器进行 Quora 发帖操作。

### 3. 流程逻辑
1. 用户运行 `start_chrome.bat` 打开一个或多个浏览器。
2. 用户手动完成登录/注册。
3. 用户运行 `auto_poster.py`。
4. `auto_poster.py` 扫描端口 -> 发现 9222 开启 -> 连接 -> 执行发帖 -> 断开 -> 扫描下一个端口 (如有)。

## 交付文件
- `start_chrome.bat`: 启动浏览器的脚本。
- `requirements.txt`: Python 依赖库 (playwright, requests)。
- `auto_poster.py`: 主程序，包含端口扫描和自动化逻辑。
