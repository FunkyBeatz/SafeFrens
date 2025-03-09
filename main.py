# main.py

import discord
from discord.ext import commands
import os
import requests

# Set up the bot with required intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Define the Verified role color
VERIFIED_ROLE_COLOR = discord.Color.from_str("#75c063")

# reCAPTCHA Site Key and Secret Key (from Google reCAPTCHA Admin Console)
RECAPTCHA_SITE_KEY = "6LfWsu4qAAAAAAghWWkYA_sk9KI-QgjGUhI6TrTD"  # Replace with your Site Key
RECAPTCHA_SECRET_KEY = os.environ.get(
    "RECAPTCHA_SECRET_KEY")  # Set in Replit secrets

# reCAPTCHA Verification URL (placeholder page to be hosted)
RECAPTCHA_VERIFY_URL = "https://your-hosted-recaptcha-page.com"  # Replace with your hosted URL


# On bot ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)


# Slash command: /frens_setup
@bot.tree.command(name="frens_setup",
                  description="Set up the Safe Frens verification system")
@app_commands.checks.has_permissions(administrator=True)
async def frens_setup(interaction: discord.Interaction):
    guild = interaction.guild

    # Create the Verified role
    verified_role = await guild.create_role(
        name="Verified",
        color=VERIFIED_ROLE_COLOR,
        reason="Created by Safe Frens bot for verification")

    # Create the verification channel
    overwrites = {
        guild.default_role:
        discord.PermissionOverwrite(view_channel=True, send_messages=False),
        guild.me:
        discord.PermissionOverwrite(view_channel=True, send_messages=True)
    }
    channel = await guild.create_text_channel("✅︳verify",
                                              overwrites=overwrites)

    # Create the initial embed with Verify and FAQ buttons
    embed = discord.Embed(
        title="Welcome to Safe Frens!",
        description=
        "In order to get full access to the server, you must complete the verification process.\n\n"
        "• Click on **Verify** to get started\n"
        "• Click on **FAQ** to learn more",
        color=discord.Color.blurple())
    # Note: Thumbnail commented out since local file paths aren't supported without a server
    embed.set_thumbnail(url="file://Assets/frens.png"
                        )  # This won't work; use an external URL instead
    # Upload frens.png to Imgur and use that URL, e.g., embed.set_thumbnail(url="https://i.imgur.com/xyz123.png")

    # Create the button view
    view = VerifyView()
    await channel.send(embed=embed, view=view)

    await interaction.response.send_message(
        "Setup complete! The verification channel has been created.",
        ephemeral=True)


# Button view for the initial embed
class VerifyView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify",
                       style=discord.ButtonStyle.primary,
                       custom_id="verify_button")
    async def verify_button(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        # Step 1: Rules embed (ephemeral)
        embed = discord.Embed(
            title="2 - Read the rules",
            description=
            "To continue, you must read and agree to the server rules.\n\n"
            "• Follow Discord's **Terms of Service** and **Community Guidelines**.\n"
            "• Treat everyone with respect. Absolutely no harassment, witch hunting, sexism, racism or hate speech will be tolerated.\n"
            "• No spam or self-promotion (server invites, advertisements, etc.) without permission. This includes DMing fellow members.\n"
            "• No age-restricted or obscene content. This includes text, images or links featuring nudity, sex, hard violence or other disturbing graphic content.\n"
            "• Not knowing the rules is not an excuse to break them. You must agree to these rules in order to get full access to the server.\n\n"
            "• Click on **Continue** if you agree to the server rules",
            color=discord.Color.blurple())
        # Note: Thumbnail commented out
        #embed.set_thumbnail(url="https://i.imgur.com/xyz123.png")  # Replace with your Imgur URL

        # Create a view for the Continue button
        view = RulesContinueView()
        await interaction.response.send_message(embed=embed,
                                                view=view,
                                                ephemeral=True)

    @discord.ui.button(label="FAQ",
                       style=discord.ButtonStyle.secondary,
                       custom_id="faq_button")
    async def faq_button(self, interaction: discord.Interaction,
                         button: discord.ui.Button):
        await interaction.response.send_message(
            "FAQ will be implemented soon!", ephemeral=True)


# View for the rules embed Continue button
class RulesContinueView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Continue",
                       style=discord.ButtonStyle.primary,
                       custom_id="rules_continue_button")
    async def continue_button(self, interaction: discord.Interaction,
                              button: discord.ui.Button):
        # Step 2: reCAPTCHA embed (ephemeral)
        embed = discord.Embed(
            title="3 - Are you human?",
            description=
            f"To continue, please complete the reCAPTCHA verification.\n\n"
            f"1. Click the **Verify with reCAPTCHA** button below.\n"
            f"2. You will be redirected to a page to complete the reCAPTCHA.\n"
            f"3. Return here and click **Submit Token** with the token provided.\n\n"
            f"reCAPTCHA Site Key: {RECAPTCHA_SITE_KEY}\n"
            f"Verification URL: {RECAPTCHA_VERIFY_URL}",
            color=discord.Color.blurple())
        # Note: Thumbnail commented out
        # embed.set_thumbnail(url="https://i.imgur.com/xyz123.png")  # Replace with your Imgur URL

        # Create a view for the reCAPTCHA steps
        view = ReCaptchaView()
        await interaction.response.send_message(embed=embed,
                                                view=view,
                                                ephemeral=True)


# View for the reCAPTCHA Submit button
class ReCaptchaView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(
            discord.ui.Button(label="Verify with reCAPTCHA",
                              style=discord.ButtonStyle.link,
                              url=RECAPTCHA_VERIFY_URL))

    @discord.ui.button(label="Submit Token",
                       style=discord.ButtonStyle.primary,
                       custom_id="recaptcha_submit")
    async def submit_button(self, interaction: discord.Interaction,
                            button: discord.ui.Button):
        # Get the token from the user's message (they'll need to paste it)
        await interaction.response.send_message(
            "Please paste the reCAPTCHA token you received and click Submit again.",
            ephemeral=True,
            view=self)
        self.waiting_for_token = True

    async def interaction_check(self, interaction: discord.Interaction):
        if self.waiting_for_token and interaction.type == discord.InteractionType.component:
            token = interaction.data.get(
                "custom_id"
            )  # This is a workaround; actual token needs user input
            if not token:
                await interaction.response.send_message(
                    "No token provided. Please paste the token and try again.",
                    ephemeral=True)
                return False

            # Verify the token with Google
            response = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": RECAPTCHA_SECRET_KEY,
                    "response":
                    token,  # This should be the user-provided token
                    "remoteip": interaction.user.
                    id  # Optional: User's IP (not directly available)
                })
            result = response.json()

            if result.get("success", False) and result.get(
                    "score", 0) >= 0.5:  # Adjust score threshold as needed
                guild = interaction.guild
                member = interaction.user
                role = discord.utils.get(guild.roles, name="Verified")
                if role:
                    await member.add_roles(
                        role, reason="Passed reCAPTCHA verification")
                    await interaction.response.send_message(
                        "Verification successful! You now have access to the server.",
                        ephemeral=True)
                else:
                    await interaction.response.send_message(
                        "Error: Verified role not found. Please contact an admin.",
                        ephemeral=True)
            else:
                await interaction.response.send_message(
                    "reCAPTCHA verification failed. Please try again.",
                    ephemeral=True)
            self.waiting_for_token = False
            return True
        return False


# Run the bot
bot.run(os.environ.get("BOT_TOKEN"))
