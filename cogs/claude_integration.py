import discord
from discord.ext import commands
import anthropic
import logging
import re

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('claude_integration')


class ClaudeIntegration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.claude = anthropic.Anthropic(
            api_key="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")
        logger.info("ClaudeIntegration cog initialized")

    @commands.Cog.listener()
    async def on_message(self, message):
        logger.debug(f"Received message: {message.content}")

        # Ignore messages from the bot itself
        if message.author == self.bot.user:
            logger.debug("Ignoring message from self")
            return

        # Check if the message is a DM or if the bot is mentioned
        if isinstance(message.channel, discord.DMChannel) or self.bot.user in message.mentions:
            logger.debug("Bot was mentioned or message is a DM")
            await self.handle_message(message)
        else:
            logger.debug("Message does not meet criteria for response")

    async def handle_message(self, message):
        logger.debug("Handling message")
        # Remove the bot mention from the message content if it exists
        content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()

        if not content:
            logger.debug("Empty content, sending default response")
            await message.channel.send("Hello! How can I assist you today?")
            return

        try:
            logger.debug("Getting Claude response")
            response = await self.get_claude_response(content)
            logger.debug(f"Sending response: {response[:50]}...")  # Log first 50 chars of response
            await message.channel.send(response)
        except Exception as e:
            logger.error(f"Error in handle_message: {e}")
            await message.channel.send(
                "I apologize, but I encountered an error while processing your request. Please try again later.")

    def clean_response(self, response):
        # Remove the TextBlock formatting if present
        cleaned = re.sub(r'^\[TextBlock\(text=\'|\'?, type=\'text\'\)\]$', '', response)
        # Remove any leading/trailing whitespace and quotes
        cleaned = cleaned.strip("'\" ")
        return cleaned

    async def get_claude_response(self, prompt):
        try:
            logger.debug(f"Sending prompt to Claude: {prompt[:50]}...")  # Log first 50 chars of prompt
            message = self.claude.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            logger.debug("Received response from Claude")
            # Extract the content from the message object
            response_content = message.content[0].text
            # Clean the response before returning
            return self.clean_response(response_content)
        except anthropic.BadRequestError as e:
            if "credit balance is too low" in str(e):
                logger.error("Insufficient credits in Anthropic account")
                return "I'm sorry, but I'm currently unable to access the Claude API due to account limitations. Please contact the bot administrator."
            else:
                logger.error(f"BadRequestError: {str(e)}")
                return "I encountered an error while processing your request. Please try again later."
        except Exception as e:
            logger.error(f"Error getting Claude response: {str(e)}")
            logger.error(f"Full exception: {repr(e)}")
            return "I'm sorry, but I couldn't generate a response at this time. Please try again later."


async def setup(bot):
    logger.info("Setting up ClaudeIntegration cog")
    await bot.add_cog(ClaudeIntegration(bot))
    logger.info("ClaudeIntegration cog setup complete")