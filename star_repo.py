import json
from openai import OpenAI
from aci import ACI
import os
from dotenv import load_dotenv

load_dotenv(verbose=True)

ACI_API_KEY = os.getenv("ACI_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Initialize OpenAI client with OpenRouter configuration
openai = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
    default_headers={
        "HTTP-Referer": "https://github.com/your-repo",  # Optional, replace with your actual site
        "X-Title": "Star Repository App",  # Optional, replace with your actual app name
    }
)
aci = ACI(api_key=ACI_API_KEY)

def main() -> None:
    # For a list of all supported apps and functions, please go to the platform.aci.dev
    print("Getting function definition for GITHUB__STAR_REPOSITORY")
    github_star_repo_function = aci.functions.get_definition("GITHUB__STAR_REPOSITORY")

    print("Sending request to OpenRouter")
    response = openai.chat.completions.create(
        model="anthropic/claude-3-opus-20240229",  # Using Claude 3 Opus via OpenRouter
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant with access to a variety of tools.",
            },
            {
                "role": "user",
                "content": "Star the aipotheosis-labs/aci github repository for me",
            },
        ],
        tools=[github_star_repo_function],
        tool_choice="required",  # force the model to generate a tool call for demo purposes
    )
    tool_call = (
        response.choices[0].message.tool_calls[0]
        if response.choices[0].message.tool_calls
        else None
    )

    if tool_call:
        print("Handling function call")
        result = aci.handle_function_call(
            tool_call.function.name,
            json.loads(tool_call.function.arguments),
            linked_account_owner_id="123"  # Replace with your actual ID
        )
        print(result)


if __name__ == "__main__":
    main()
