import json
from openai import OpenAI
from aci import ACI
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv(verbose=True)

ACI_API_KEY = os.getenv("ACI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 初始化OpenAI客户端（使用OpenRouter）
openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/your-repo",
        "X-Title": "Paper Search and Email App",
    }
)
aci = ACI(api_key=ACI_API_KEY)

def format_email_content(papers):
    """格式化邮件内容"""
    email_content = "最新研究论文摘要：\n\n"
    for i, paper in enumerate(papers, 1):
        email_content += f"{i}. {paper.get('title', 'No Title')}\n"
        email_content += f"作者: {', '.join(paper.get('authors', ['Unknown']))}\n"
        email_content += f"链接: {paper.get('url', 'No URL')}\n"
        email_content += f"摘要: {paper.get('summary', 'No abstract available')}\n\n"
    return email_content

def main(query: str, email_to: str) -> None:
    # 获取ArXiv搜索功能定义
    print("获取ArXiv搜索功能定义")
    arxiv_search_function = {
        "name": "ARXIV__SEARCH_PAPERS",
        "description": "Search for papers on ArXiv",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results to return"
                }
            },
            "required": ["query"]
        }
    }

    # 获取Gmail发送功能定义
    print("获取Gmail发送功能定义")
    gmail_send_function = {
        "name": "GMAIL__SEND_EMAIL",
        "description": "Send an email via Gmail",
        "parameters": {
            "type": "object",
            "properties": {
                "to": {
                    "type": "string",
                    "description": "Recipient email address"
                },
                "subject": {
                    "type": "string",
                    "description": "Email subject"
                },
                "body": {
                    "type": "string",
                    "description": "Email body content"
                }
            },
            "required": ["to", "subject", "body"]
        }
    }

    print("发送请求到OpenRouter进行论文搜索")
    search_response = openai.chat.completions.create(
        model="anthropic/claude-3-opus-20240229",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的研究助手，可以搜索和总结学术论文。请使用ArXiv API搜索论文。",
            },
            {
                "role": "user",
                "content": query,
            },
        ],
        tools=[arxiv_search_function],
        tool_choice="required",
    )

    search_tool_call = (
        search_response.choices[0].message.tool_calls[0]
        if search_response.choices[0].message.tool_calls
        else None
    )

    if search_tool_call:
        print("处理ArXiv搜索请求")
        search_args = json.loads(search_tool_call.function.arguments)
        if "max_results" not in search_args:
            search_args["max_results"] = 5

        search_result = aci.handle_function_call(
            search_tool_call.function.name,
            search_args,
            linked_account_owner_id="123"  # 替换为实际ID
        )

        # 格式化邮件内容
        papers = search_result.get('entries', [])  # 使用entries而不是papers
        email_content = format_email_content(papers)

        print("发送请求到OpenRouter进行邮件发送")
        email_response = openai.chat.completions.create(
            model="anthropic/claude-3-opus-20240229",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个邮件助手，负责发送邮件。",
                },
                {
                    "role": "user",
                    "content": f"请将以下内容发送到{email_to}：\n\n{email_content}",
                },
            ],
            tools=[gmail_send_function],
            tool_choice="required",
        )

        email_tool_call = (
            email_response.choices[0].message.tool_calls[0]
            if email_response.choices[0].message.tool_calls
            else None
        )

        if email_tool_call:
            print("发送邮件")
            email_args = json.loads(email_tool_call.function.arguments)
            if "subject" not in email_args:
                email_args["subject"] = "最新ArXiv论文搜索结果"

            email_result = aci.handle_function_call(
                email_tool_call.function.name,
                email_args,
                linked_account_owner_id="123"  # 替换为实际ID
            )
            print("邮件发送结果：", email_result)

if __name__ == "__main__":
    # 示例使用
    query = "Search for 5 recent RL papers in 2025"
    email_to = os.getenv("RECIPIENT_EMAIL")
    main(query, email_to)
