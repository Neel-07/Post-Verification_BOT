import discord
from discord.ext import commands
import os
import asyncio
import re

# Intents
intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.message_content = True

# Bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Store eligible user IDs
eligible_users = set()

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
async def info(ctx):
    await ctx.send('I am a Discord bot that verifies the post for different challenges and maintains your streak!')

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
            await ctx.send("Your post format is incorrect. Please follow the guidelines, and make sure to include either a LinkedIn or Twitter link.")
    else:
        await ctx.send("Please include the #30DaysOfCode hashtag in your post to count it.")



def is_valid_post(message):
    # Implement format checks here (e.g., attachment checks, character count checks)
    content = message.content # Convert to lowercase for case-insensitive checks

    # Define regex patterns for LinkedIn and Twitter links
    linkedin_pattern = r"https://www\.linkedin\.com/in/[A-Za-z0-9-]+"
    twitter_pattern = r"https://twitter\.com/[A-Za-z0-9_]+"

    # Use re.search to find a LinkedIn or Twitter link in the message content
    linkedin_match = re.search(linkedin_pattern, content)
    twitter_match = re.search(twitter_pattern, content)

    # Print the matched links for debugging
    print(f"Content: {content}")
    print(f"LinkedIn Match: {linkedin_match}")
    print(f"Twitter Match: {twitter_match}")

    # Check for the presence of required hashtags
    required_hashtags = ["#30DaysOfCode"]
    
    # Print the result of hashtag check for debugging
    print(f"Hashtag Check: {all(hashtag in content for hashtag in required_hashtags)}")

    # Check if at least one of the patterns or the required hashtags is found
    if (linkedin_match is not None or twitter_match is not None) and all(hashtag in content for hashtag in required_hashtags):
        return True
    else:
        return False


class Event:
    def __init__(self, name, format, duration_days, eligibility_criteria):
        self.name = name
        self.format = format
        self.duration_days = duration_days
        self.eligibility_criteria = eligibility_criteria
        self.start_time = None  # Timestamp when the event starts
        self.participants = set()  # Store user IDs who have posted for this event


events = []  # List to store active events

@bot.command()
async def createevent(ctx, name, format, duration_days: int, eligibility_criteria: int):
    # Check if the user is an administrator
    if any(role.name == "Administrator" for role in ctx.author.roles):
        # Validate input
        if duration_days <= 0 or eligibility_criteria < 0:
            await ctx.send("Invalid input. Duration days should be greater than 0, and eligibility criteria should be non-negative.")
            return

        # Check if an event with the same name already exists
        for event in events:
            if event.name == name:
                await ctx.send("An event with the same name already exists.")
                return

        # Create and add the event
        event = Event(name, format, duration_days, eligibility_criteria)
        events.append(event)

        await ctx.send(f"Event '{name}' created.")
    else:
        await ctx.send("You do not have permission to create events.")



# You would need functions to start and stop events, track user participation, validate posts, etc.


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
    if any(role.name == "Administrator" for role in ctx.author.roles):
        if eligible_users:
            eligible_list = "\n".join([str(user) for user in eligible_users])
            await ctx.send("Eligible participants list:\n" + eligible_list)
        else:
            await ctx.send("There are no eligible participants.")
        # Export the list to a text file
        with open("eligible_participants.txt", "w") as file:
            if eligible_users:
                file.write(eligible_list)
            else:
                file.write("No eligible participants.")
        await ctx.send("Eligible participants list exported as eligible_participants.txt.")
    else:
        await ctx.send("You do not have permission to view the list.")



# Function to get eligible users (You need to implement this function)
def get_eligible_users():
    eligible_users = []

    # Add logic here to determine eligible users
    for user_id in eligible_users:
        if is_user_eligible(user_id):
            eligible_users.append(user_id)

    return eligible_users

def is_user_eligible(user_id):
    # Check if the user has participated in at least 5 valid posts
    if get_valid_post_count(user_id) >= 5:
        return True
    else:
        return False

# Example function to get the count of valid posts for a user
def get_valid_post_count(user_id):
    # Implement logic to retrieve the count of valid posts for the user
    # For example, you can query a database or keep track of it in your bot's data
    # Return the count of valid posts
    pass

@bot.command()
async def distribute_tokens(ctx, amount: int):
    # Check if the user has the necessary permissions (e.g., server administrators)
    if any(role.name == "Administrator" for role in ctx.author.roles):
        eligible_users = get_eligible_users()  # You should implement this function to fetch eligible users
        total_users = len(eligible_users)

        if total_users > 0:
            tokens_per_user = amount // total_users  # Integer division to evenly distribute tokens
            failed_users = []

            for user_id in eligible_users:
                try:
                    # Implement logic to distribute tokens to eligible users
                    # Update user token balances here
                    pass  # Replace with your distribution logic
                except Exception as e:
                    # If an error occurs while distributing tokens to a user, log the error and continue
                    print(f"Error distributing tokens to user {user_id}: {str(e)}")
                    failed_users.append(user_id)

            if failed_users:
                await ctx.send(f"{amount} tokens distributed to eligible participants, but there were errors for some users.")
    else:
        await ctx.send("You do not have permission to distribute tokens.")

reminders = {}

@bot.command()
async def remindme(ctx):
    user_id = ctx.author.id

    # Check if the user is already scheduled for reminders
    if user_id not in reminders:
        reminders[user_id] = bot.loop.create_task(send_daily_reminder(ctx))
        await ctx.send("You will receive daily reminders to post.")
    else:
        await ctx.send("You are already scheduled to receive reminders.")

async def send_daily_reminder(ctx):
    while True:
        # Send the reminder message
        await ctx.send("Don't forget to post today!")

        # Wait for 24 hours before sending the next reminder
        await asyncio.sleep(86400)  # 24 hours




@bot.command()
async def noremind(ctx):
    user_id = ctx.author.id

    if user_id in reminders:
        reminders[user_id].cancel()
        del reminders[user_id]
        await ctx.send("You will no longer receive daily reminders.")
    else:
        await ctx.send("You don't have any active reminders.")



# Run the bot with the token stored in the environment variable
bot.run('MTE1NzcwNDU5NDExNDIzMjQ1MQ.GK6Acc.qVulN2xf9o1Et8v0MAarSJgXK5zuzJXx8sTBzw')

