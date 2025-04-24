import json
from openai import OpenAI
from aci import ACI
import os
from dotenv import load_dotenv
import xml.etree.ElementTree as ET
from datetime import datetime

load_dotenv(verbose=True)

ACI_API_KEY = os.getenv("ACI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

print("环境变量检查:")
print(f"ACI_API_KEY 是否存在: {'是' if ACI_API_KEY else '否'}")
print(f"OPENROUTER_API_KEY 是否存在: {'是' if OPENROUTER_API_KEY else '否'}")

# 初始化 OpenAI 客户端
openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/your-repo",
        "X-Title": "Arxiv Search App",
    }
)
aci = ACI(api_key=ACI_API_KEY)

def parse_arxiv_xml(xml_data):
    """解析Arxiv XML响应"""
    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
        paper = {
            'title': entry.find('{http://www.w3.org/2005/Atom}title').text.strip(),
            'abstract': entry.find('{http://www.w3.org/2005/Atom}summary').text.strip(),
            'url': entry.find('{http://www.w3.org/2005/Atom}id').text
        }
        papers.append(paper)

    return papers

def search_papers(topic: str) -> None:
    """
    搜索特定主题的最新论文

    Args:
        topic: 搜索主题
    """
    print(f"\n开始搜索流程:")
    print(f"1. 搜索主题: {topic}")

    try:
        # 获取 Arxiv 搜索函数定义
        print("\n2. 获取 ARXIV__SEARCH_PAPERS 函数定义")
        arxiv_search_function = aci.functions.get_definition("ARXIV__SEARCH_PAPERS")
        print(f"函数定义获取成功: {arxiv_search_function.get('name', 'Unknown')}")
        print(f"函数参数: {json.dumps(arxiv_search_function.get('parameters', {}), indent=2, ensure_ascii=False)}")

        print("\n3. 创建 OpenAI 请求")
        messages = [
            {
                "role": "system",
                "content": "你是一个帮助搜索学术论文的助手。请使用ARXIV__SEARCH_PAPERS函数搜索论文。",
            },
            {
                "role": "user",
                "content": f"搜索关于 {topic} 的最新论文，按时间排序，返回最新的10篇论文。",
            },
        ]
        print(f"请求消息: {json.dumps(messages, indent=2, ensure_ascii=False)}")

        response = openai.chat.completions.create(
            model="anthropic/claude-3-opus-20240229",
            messages=messages,
            tools=[arxiv_search_function],
            tool_choice="required",
        )

        print("\n4. OpenAI 响应:")
        print(f"响应状态: {response.model_dump_json()}")

        tool_call = (
            response.choices[0].message.tool_calls[0]
            if response.choices[0].message.tool_calls
            else None
        )

        if tool_call:
            print("\n5. 处理工具调用:")
            print(f"调用函数: {tool_call.function.name}")
            print(f"函数参数: {tool_call.function.arguments}")

            result = aci.handle_function_call(
                tool_call.function.name,
                json.loads(tool_call.function.arguments),
                linked_account_owner_id="123"
            )

            print("\n6. ACI 响应结果:")
            print(f"原始响应: {json.dumps(result, indent=2, ensure_ascii=False)}")

            if isinstance(result, dict) and 'data' in result:
                papers = parse_arxiv_xml(result['data'])[:5]  # 只取前5篇论文
                print(f"\n找到 {len(papers)} 篇相关论文:")
                print("=" * 80)

                for i, paper in enumerate(papers, 1):
                    print(f"\n论文 {i}:")
                    print(f"标题: {paper['title']}")
                    print(f"摘要: {paper['abstract']}")
                    print(f"URL: {paper['url']}")
                    print("-" * 80)
            else:
                print("\n未找到相关论文")
        else:
            print("\n搜索失败，请稍后重试")

    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        raise

def main():
    topic = input("请输入要搜索的主题: ")
    search_papers(topic)

if __name__ == "__main__":
    main()
