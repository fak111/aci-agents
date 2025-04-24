# ArXiv Paper Search and Email Tool

This is an automated tool that can:
1. Search for the latest papers on ArXiv
2. Send search results via Gmail to a specified email address

## Requirements
- Python 3.8+
- Required API keys (configured in the .env file)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/fak111/aci-agents.git
cd aci-agents
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a .env file with the following content:
```
ACI_API_KEY=your_aci_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
GMAIL_SENDER=your_gmail_address
RECIPIENT_EMAIL=recipient_email_address
GMAIL_APP_PASSWORD=your_gmail_app_password
```

## Usage

1. Run scripts directly:
```bash
uv run search_paper.py
# or
uv run arxiv_gmail.py
```

2. Import as a module:
```python
from search_paper import main

main("Search for 5 recent RL papers in 2025", "your-email@example.com")
```

## Notes
- Ensure you have the correct API keys and permissions
- Gmail API requires proper authorization
- ArXiv API may have usage limitations

## Features
- Support for custom search queries
- Automatic email content formatting
- Includes paper titles, authors, links, and abstracts
- Uses Claude 3 Opus for intelligent processing
