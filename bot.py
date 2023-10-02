import discord
from discord.ext import commands
import os
import asyncio

intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

# Store eligible user IDs
eligible_users = set()

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def info(ctx):
    await ctx.send('I am a Discord bot that can do cool things!')

@bot.command()
async def post(ctx):
    # Check if the message contains the #30DaysOfCode hashtag
    if "#30DaysOfCode" in ctx.message.content:
        # Check for additional format criteria
        if is_valid_post(ctx.message):
            update_streak(ctx.author.id)
            eligible_users.add(ctx.author.id)  # Mark user as eligible
            await ctx.send("Your daily post for the #30DaysOfCode challenge has been counted!")
        else:
            await ctx.send("Your post format is incorrect. Please follow the guidelines.")
    else:
        await ctx.send("Please include the #30DaysOfCode hashtag in your post to count it.")

# Define the is_valid_post function for format checks
def is_valid_post(message):
    # Implement format checks here (e.g., attachment checks, character count checks)
    content = message.content.lower()  # Convert to lowercase for case-insensitive checks

    # Check if the post contains a screenshot or attachment
    if not any(attachment.url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) for attachment in message.attachments):
        return False  # No valid screenshot or attachment found

    # Check for the presence of required hashtags
    required_hashtags = ["#30daysofcode"]
    if not all(hashtag in content for hashtag in required_hashtags):
        return False  # Missing required hashtags

    # You can add more checks here as needed (e.g., minimum character count)

    return True  # All format checks passed


# Function to update the user's streak
streaks = {}

def update_streak(user_id):
    if user_id not in streaks:
        streaks[user_id] = 1
    else:
        streaks[user_id] += 1

@bot.command()
async def mystreak(ctx):
    user_id = ctx.author.id

    # Check if the user has a streak
    if user_id in streaks:
        await ctx.send(f"Your current streak is {streaks[user_id]} days.")
    else:
        await ctx.send("You don't have an active streak.")


@bot.command()
async def eligibility(ctx):
    if ctx.author.id in eligible_users:
        await ctx.send("You are eligible for rewards!")
    else:
        await ctx.send("You are not eligible for rewards.")

@bot.command()
async def export(ctx):
    # Check if the user has the necessary permissions (e.g., server moderators)
    if any(role.name == "Moderator" for role in ctx.author.roles):
        eligible_list = "\n".join([str(user) for user in eligible_users])
        with open("eligible_participants.txt", "w") as file:
            file.write(eligible_list)
        await ctx.send("Eligible participants list exported as eligible_participants.txt.")
    else:
        await ctx.send("You do not have permission to export the list.")


@bot.command()
async def distribute_tokens(ctx, amount: int):
    # Check if the user has the necessary permissions (e.g., server administrators)
    if any(role.name == "Administrator" for role in ctx.author.roles):
        for user_id in eligible_users:
            # Implement logic to distribute tokens to eligible users
            # Update user token balances here
            pass  # Replace with your distribution logic
        await ctx.send(f"{amount} tokens distributed to eligible participants.")
    else:
        await ctx.send("You do not have permission to distribute tokens.")


@bot.command()
async def remindme(ctx):
    user_id = ctx.author.id
    await ctx.send("You will receive daily reminders to post.")
    while True:
        await asyncio.sleep(86400)  # 24 hours (adjust as needed)
        if user_id not in eligible_users:
            await ctx.send("Don't forget to post today!")

@bot.command()
async def noremind(ctx):
    await ctx.send("You will no longer receive daily reminders.")
    # Remove the user from the reminders list (implement this logic)


# Run the bot with the token stored in the environment variable
bot.run('MTE1NzcwNDU5NDExNDIzMjQ1MQ.GaCqPw.SezY_UHVLARK0gEHOqCXQtHY3VZJT53Ibs_Lek')

