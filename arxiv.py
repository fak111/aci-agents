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

print("Environment variables check:")
print(f"ACI_API_KEY exists: {'Yes' if ACI_API_KEY else 'No'}")
print(f"OPENROUTER_API_KEY exists: {'Yes' if OPENROUTER_API_KEY else 'No'}")

# Initialize OpenAI client
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
    """Parse Arxiv XML response"""
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
    Search for the latest papers on a specific topic

    Args:
        topic: search topic
    """
    print(f"\nStarting search process:")
    print(f"1. Search topic: {topic}")

    try:
        # Get Arxiv search function definition
        print("\n2. Getting ARXIV__SEARCH_PAPERS function definition")
        arxiv_search_function = aci.functions.get_definition("ARXIV__SEARCH_PAPERS")
        print(f"Function definition retrieved successfully: {arxiv_search_function.get('name', 'Unknown')}")
        print(f"Function parameters: {json.dumps(arxiv_search_function.get('parameters', {}), indent=2, ensure_ascii=False)}")

        print("\n3. Creating OpenAI request")
        messages = [
            {
                "role": "system",
                "content": "You are an assistant that helps search for academic papers. Please use the ARXIV__SEARCH_PAPERS function to search for papers.",
            },
            {
                "role": "user",
                "content": f"Search for the latest papers on {topic}, sorted by time, and return the 10 most recent papers.",
            },
        ]
        print(f"Request messages: {json.dumps(messages, indent=2, ensure_ascii=False)}")

        response = openai.chat.completions.create(
            model="anthropic/claude-3-opus-20240229",
            messages=messages,
            tools=[arxiv_search_function],
            tool_choice="required",
        )

        print("\n4. OpenAI response:")
        print(f"Response status: {response.model_dump_json()}")

        tool_call = (
            response.choices[0].message.tool_calls[0]
            if response.choices[0].message.tool_calls
            else None
        )

        if tool_call:
            print("\n5. Processing tool call:")
            print(f"Function called: {tool_call.function.name}")
            print(f"Function arguments: {tool_call.function.arguments}")

            result = aci.handle_function_call(
                tool_call.function.name,
                json.loads(tool_call.function.arguments),
                linked_account_owner_id="123"
            )

            print("\n6. ACI response result:")
            print(f"Raw response: {json.dumps(result, indent=2, ensure_ascii=False)}")

            if isinstance(result, dict) and 'data' in result:
                papers = parse_arxiv_xml(result['data'])[:5]  # Only take first 5 papers
                print(f"\nFound {len(papers)} relevant papers:")
                print("=" * 80)

                for i, paper in enumerate(papers, 1):
                    print(f"\nPaper {i}:")
                    print(f"Title: {paper['title']}")
                    print(f"Abstract: {paper['abstract']}")
                    print(f"URL: {paper['url']}")
                    print("-" * 80)
            else:
                print("\nNo relevant papers found")
        else:
            print("\nSearch failed, please try again later")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

def main():
    topic = input("Please enter the topic to search: ")
    search_papers(topic)

if __name__ == "__main__":
    main()
