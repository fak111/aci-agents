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

# Initialize OpenAI client with OpenRouter configuration
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
    # Get email sending function definition
    print("Getting GMAIL__SEND_EMAIL function definition")
    gmail_send_email_function = aci.functions.get_definition("GMAIL__SEND_EMAIL")

    print("Sending request to OpenRouter")
    response = openai.chat.completions.create(
        model="anthropic/claude-3-opus-20240229",
        messages=[
            {
                "role": "system",
                "content": f"You are an email assistant. You will send emails as {GMAIL_SENDER} to {RECIPIENT_EMAIL}. Please generate and send emails based on user requests.",
            },
            {
                "role": "user",
                "content": "Send a test email explaining that this is an automatically sent test email.",
            },
        ],
        tools=[gmail_send_email_function],
        tool_choice="required",  # Force the model to generate a tool call
    )
    tool_call = (
        response.choices[0].message.tool_calls[0]
        if response.choices[0].message.tool_calls
        else None
    )

    if tool_call:
        print("Processing function call")
        args = json.loads(tool_call.function.arguments)
        # Ensure using email addresses from environment variables
        args["sender"] = GMAIL_SENDER
        args["recipient"] = RECIPIENT_EMAIL

        result = aci.handle_function_call(
            tool_call.function.name,
            args,
            linked_account_owner_id="123"  # Replace with your actual ID
        )
        print(result)

if __name__ == "__main__":
    main()
