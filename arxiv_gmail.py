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
GMAIL_SENDER = os.getenv("GMAIL_SENDER")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

# Initialize OpenAI client
openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/your-repo",
        "X-Title": "Arxiv Gmail Agent",
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

def search_and_send_papers(topic: str) -> None:
    """
    Search for latest papers on a specific topic and send via email

    Args:
        topic: search topic
    """
    print(f"\nStarting search process:")
    print(f"1. Search topic: {topic}")

    try:
        # Get function definitions
        print("\n2. Getting function definitions")
        arxiv_search_function = aci.functions.get_definition("ARXIV__SEARCH_PAPERS")
        gmail_send_email_function = aci.functions.get_definition("GMAIL__SEND_EMAIL")

        # Step 1: Search papers
        print("\n3. Executing Arxiv search")
        arxiv_args = {
            "query": {
                "search_query": topic,
                "sortBy": "lastUpdatedDate",
                "sortOrder": "descending",
                "max_results": 10
            }
        }

        arxiv_result = aci.handle_function_call(
            "ARXIV__SEARCH_PAPERS",
            arxiv_args,
            linked_account_owner_id="123"
        )

        if isinstance(arxiv_result, dict) and 'data' in arxiv_result:
            papers = parse_arxiv_xml(arxiv_result['data'])[:5]  # Only take first 5 papers

            # Prepare email content
            email_content = f"Latest paper search results for {topic}:\n\n"
            for i, paper in enumerate(papers, 1):
                email_content += f"Paper {i}:\n"
                email_content += f"Title: {paper['title']}\n"
                email_content += f"Abstract: {paper['abstract']}\n"
                email_content += f"URL: {paper['url']}\n\n"

            # Step 2: Send email
            print("\n4. Sending email")
            email_args = {
                "sender": GMAIL_SENDER,
                "recipient": RECIPIENT_EMAIL,
                "subject": f"Latest Paper Search Results for {topic}",
                "body": email_content
            }

            email_result = aci.handle_function_call(
                "GMAIL__SEND_EMAIL",
                email_args,
                linked_account_owner_id="123"
            )
            print(f"Email sending result: {email_result}")
        else:
            print("\nNo relevant papers found")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

def main():
    topic = input("Please enter the topic to search: ")
    search_and_send_papers(topic)

if __name__ == "__main__":
    main()
