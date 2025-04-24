# ArXiv论文搜索和邮件发送工具

这是一个自动化工具，可以：
1. 搜索ArXiv上的最新论文
2. 将搜索结果通过Gmail发送到指定邮箱

## 环境要求
- Python 3.8+
- 必要的API密钥（在.env文件中配置）

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/fak111/aci-agents.git
cd aci-agents
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建一个.env文件，包含以下内容：
```
ACI_API_KEY=your_aci_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
GMAIL_SENDER=your_gmail_address
RECIPIENT_EMAIL=recipient_email_address
GMAIL_APP_PASSWORD=your_gmail_app_password
```

## 使用方法

1. 直接运行脚本：
```bash
uv run search_paper.py
# 或者
uv run arxiv_gmail.py
```

2. 作为模块导入：
```python
from search_paper import main

main("Search for 5 recent RL papers in 2025", "your-email@example.com")
```

## 注意事项
- 确保您有正确的API密钥和权限
- Gmail API需要适当的授权
- ArXiv API可能有使用限制

## 功能特点
- 支持自定义搜索查询
- 自动格式化邮件内容
- 包含论文标题、作者、链接和摘要
- 使用Claude 3 Opus进行智能处理
