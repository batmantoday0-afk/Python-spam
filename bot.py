import asyncio
from discord.ext import commands
import discord
import random
import time

# Logging helper
def log(msg):
    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

# Load messages
with open("messages.txt", "r", encoding="utf-8") as f:
    messages = [line.strip() for line in f if line.strip()]

async def start_bot(token):
    bot = commands.Bot(command_prefix="!", self_bot=True)
    spam_channels = []

    @bot.event
    async def on_ready():
        log(f"[+] Logged in as {bot.user}")
        
        # Find all channels named "spam" (case-insensitive)
        for guild in bot.guilds:
            for channel in guild.text_channels:
                if channel.name.lower() == "spam":
                    spam_channels.append(channel)
                    log(f"[{bot.user}] Found spam channel in {guild.name}: #{channel.name}")
        
        if not spam_channels:
            log(f"[{bot.user}] No 'spam' channels found in any server!")
        else:
            log(f"[{bot.user}] Found {len(spam_channels)} spam channel(s)")
            asyncio.create_task(send_loop(bot))

    @bot.event
    async def on_guild_join(guild):
        # Check for spam channel when joining a new server
        for channel in guild.text_channels:
            if channel.name.lower() == "spam":
                spam_channels.append(channel)
                log(f"[{bot.user}] Found spam channel in new server {guild.name}: #{channel.name}")

    @bot.event
    async def on_disconnect():
        log(f"[{bot.user}] Disconnected. Trying to reconnect...")

    @bot.event
    async def on_error(event, *args, **kwargs):
        log(f"[{bot.user}] Error in event {event}")

    async def send_loop(bot):
        while True:
            try:
                if spam_channels:
                    # Send to all spam channels found
                    for channel in spam_channels:
                        try:
                            msg = random.choice(messages)
                            await channel.send(msg)
                        except discord.HTTPException as e:
                            log(f"[{bot.user}] HTTP error in {channel.guild.name}: {e}")
                        except Exception as e:
                            log(f"[{bot.user}] Error in {channel.guild.name}: {e}")
            except Exception as e:
                log(f"[{bot.user}] Unexpected error: {e}")
            await asyncio.sleep(3)  # 2 seconds 

    while True:
        try:
            await bot.start(token)
        except Exception as e:
            log(f"[{token[:10]}...] Reconnect failed: {e}")
            await asyncio.sleep(10)

async def main():
    tasks = []
    with open("tokens.txt", "r") as f:
        for line in f:
            token = line.strip()
            if token:  # Skip empty lines
                tasks.append(asyncio.create_task(start_bot(token)))
    await asyncio.gather(*tasks)

# Start everything
asyncio.run(main())
