# Safe Frens Bot

A Discord verification bot built with Python and discord.py. This bot provides a verification system for Discord servers under the Webfrens umbrella.

## Features
- Slash command `/frens_setup` to create a verification channel and role.
- Embed-based verification process with rules and a captcha.
- Assigns a "Verified" role upon successful verification.

## Setup
1. Clone the repository.
2. Install dependencies: `pip install discord.py`
3. Set the `BOT_TOKEN` environment variable with your Discord bot token.
4. Run the bot: `python main.py`

## Requirements
- Python 3.8+
- discord.py

## To-Do
- Add FAQ functionality.
- Implement "More Info" section.
- Expand captcha image database.