import json
from openai import OpenAI
from aci import ACI
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv(verbose=True)

ACI_API_KEY = os.getenv("ACI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenAI client (using OpenRouter)
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
    """Format email content"""
    email_content = "Latest Research Paper Summaries:\n\n"
    for i, paper in enumerate(papers, 1):
        email_content += f"{i}. {paper.get('title', 'No Title')}\n"
        email_content += f"Authors: {', '.join(paper.get('authors', ['Unknown']))}\n"
        email_content += f"Link: {paper.get('url', 'No URL')}\n"
        email_content += f"Abstract: {paper.get('summary', 'No abstract available')}\n\n"
    return email_content

def main(query: str, email_to: str) -> None:
    # Get ArXiv search function definition
    print("Getting ArXiv search function definition")
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

    # Get Gmail sending function definition
    print("Getting Gmail sending function definition")
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

    print("Sending request to OpenRouter for paper search")
    search_response = openai.chat.completions.create(
        model="anthropic/claude-3-opus-20240229",
        messages=[
            {
                "role": "system",
                "content": "You are a professional research assistant who can search and summarize academic papers. Please use the ArXiv API to search for papers.",
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
        print("Processing ArXiv search request")
        search_args = json.loads(search_tool_call.function.arguments)
        if "max_results" not in search_args:
            search_args["max_results"] = 5

        search_result = aci.handle_function_call(
            search_tool_call.function.name,
            search_args,
            linked_account_owner_id="123"  # Replace with actual ID
        )

        # Format email content
        papers = search_result.get('entries', [])  # Use entries instead of papers
        email_content = format_email_content(papers)

        print("Sending request to OpenRouter for email sending")
        email_response = openai.chat.completions.create(
            model="anthropic/claude-3-opus-20240229",
            messages=[
                {
                    "role": "system",
                    "content": "You are an email assistant responsible for sending emails.",
                },
                {
                    "role": "user",
                    "content": f"Please send the following content to {email_to}:\n\n{email_content}",
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
            print("Sending email")
            email_args = json.loads(email_tool_call.function.arguments)
            if "subject" not in email_args:
                email_args["subject"] = "Latest ArXiv Paper Search Results"

            email_result = aci.handle_function_call(
                email_tool_call.function.name,
                email_args,
                linked_account_owner_id="123"  # Replace with actual ID
            )
            print("Email sending result:", email_result)

if __name__ == "__main__":
    # Example usage
    query = "Search for 5 recent RL papers in 2025"
    email_to = os.getenv("RECIPIENT_EMAIL")
    main(query, email_to)
