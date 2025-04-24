import json
from openai import OpenAI
from aci import ACI
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

ACI_API_KEY = os.getenv("ACI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GMAIL_SENDER = os.getenv("GMAIL_SENDER")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# 初始化 OpenAI client，使用 OpenRouter 配置
openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/your-repo",
        "X-Title": "Email Agent App",
    }
)
aci = ACI(api_key=ACI_API_KEY)

def main() -> None:
    # 获取发送邮件的函数定义
    print("获取 GMAIL__SEND_EMAIL 函数定义")
    gmail_send_email_function = aci.functions.get_definition("GMAIL__SEND_EMAIL")

    print("向 OpenRouter 发送请求")
    response = openai.chat.completions.create(
        model="anthropic/claude-3-opus-20240229",
        messages=[
            {
                "role": "system",
                "content": f"你是一个邮件助手。你将使用 {GMAIL_SENDER} 的身份发送邮件给 {RECIPIENT_EMAIL}。请根据用户的需求生成并发送邮件。",
            },
            {
                "role": "user",
                "content": "发送一封测试邮件，介绍一下这是自动发送的测试邮件。",
            },
        ],
        tools=[gmail_send_email_function],
        tool_choice="required",  # 强制模型生成工具调用
    )
    tool_call = (
        response.choices[0].message.tool_calls[0]
        if response.choices[0].message.tool_calls
        else None
    )

    if tool_call:
        print("处理函数调用")
        args = json.loads(tool_call.function.arguments)
        # 确保使用环境变量中的邮箱地址
        args["sender"] = GMAIL_SENDER
        args["recipient"] = RECIPIENT_EMAIL

        result = aci.handle_function_call(
            tool_call.function.name,
            args,
            linked_account_owner_id="123"  # 替换为你的实际 ID
        )
        print(result)

if __name__ == "__main__":
    main()
