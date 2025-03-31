# EAGv1-Assignment4: Agentic Workflow Client

This project implements an agentic workflow client that uses Google's Gemini AI model to interact with a server through the Model Control Protocol (MCP). The client can perform various tasks including drawing, sending emails, and executing commands based on natural language instructions.

## Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Mission Control Protocol (MCP) server running

## Setup Instructions

1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following variables:
```
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-2.0-flash  # or your preferred model
```

## Project Structure

- `mcp_client.py`: Main client implementation
- `mcp_server.py`: Server implementation
- `send_email.py`: Email functionality
- `use_paint_preview_with_mac.py`: Drawing functionality
- `.env`: Environment variables (create this file)

## Usage

1. First, start the MCP server:
```bash
mcp dev mcp_server.py
```
This will allow you to visualize all the tools and functionalities in the MCP Inspector

2. In a new terminal, run the client:
```bash
python mcp_client.py
```

## Features

- Natural language processing using Google's Gemini AI
- Drawing capabilities using Python's built-in drawing functions
- Email sending functionality
- Command execution
- Interactive conversation with the AI agent
- Timeout handling for API calls
- Colored console output for better readability


## Logging

- The interactions with the LLM are logged for better understanding what happened in each iteration

## Notes

- Make sure your Gemini API key is valid and has sufficient quota
- Some features may require additional system permissions (e.g., drawing, command execution)

## Troubleshooting

If you encounter issues:
1. Verify your API key in the `.env` file
2. Ensure all dependencies are installed correctly
3. Check the `logs/llm_logs.log` file for getting the flow of functions called by agent
4. To use the email functionality, your `.env` file must also contain the keys: MODEL_NAME,  SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, DEFAULT_RECIPIENT
