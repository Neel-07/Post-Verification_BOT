import discord
from discord.ext import commands
import os
import asyncio
import re
import datetime  # Import datetime module for date and time operations
import csv

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

event_data = {}

@bot.command()
async def post(ctx, event_name: str, *, message_content: str):
    # Extract the event hashtag from the message content
    # Assuming that the hashtag is at the end of the message_content
    parts = message_content.split()
    event_hashtag = parts[-1] if parts and parts[-1].startswith("#") else ""

    # Check if the event exists
    if event_name not in event_data:
        await ctx.send(f"The event '{event_name}' does not exist.")
        return

    # Check if the message contains the event hashtag
    if event_hashtag:
        # Check for additional format criteria
        if is_valid_post(message_content, event_name, event_hashtag):
            update_streak(ctx.author.id, event_name)
            eligible_users.add(ctx.author.id)  # Mark the user as eligible
            await ctx.send(f"Your daily post for the {event_hashtag} challenge has been counted!")
        else:
            await ctx.send(f"Your post format is incorrect. Please follow the guidelines and make sure to include either a LinkedIn or Twitter link along with the {event_hashtag} hashtag.")
    else:
        await ctx.send(f"Please include a valid event hashtag (e.g., #PhotoFun) in your post to count it.")










def is_valid_post(message_content, event_name, event_hashtag):
    # Implement format checks here (e.g., attachment checks, character count checks)
    content = message_content.lower()  # Convert to lowercase for case-insensitive checks

    # Define regex patterns for LinkedIn and Twitter links
    linkedin_pattern = r"https://www\.linkedin\.com/in/[A-Za-z0-9-]+"
    twitter_pattern = r"https://twitter\.com/[A-Za-z0-9_]+"

    # Use re.search to find a LinkedIn or Twitter link in the message content
    linkedin_match = re.search(linkedin_pattern, content)
    twitter_match = re.search(twitter_pattern, content)

    # Check for the presence of required hashtags (including the event hashtag)
    required_hashtags = [f"{event_hashtag.lower()}"]  # Convert the event hashtag to lowercase
    
    # Check if at least one of the patterns or the required hashtags is found
    if (linkedin_match is not None or twitter_match is not None) and all(hashtag in content for hashtag in required_hashtags):
        return True
    else:
        return False


class Event:
    def __init__(self, name, format, duration_days, eligibility_criteria, post_hashtag):
        self.name = name
        self.format = format
        self.duration_days = duration_days
        self.eligibility_criteria = eligibility_criteria
        self.post_hashtag = post_hashtag  # Add a new attribute for post hashtag
        self.start_time = None  # Timestamp when the event starts



events = []  # List to store active events

@bot.command()
async def createevent(ctx, event_name: str, event_format: str, duration_days: int, eligibility_criteria: int, event_hashtag: str):
    # Check if the user is an administrator
    if any(role.name == "Administrator" for role in ctx.author.roles):
        # Validate input
        if duration_days <= 0 or eligibility_criteria < 0:
            await ctx.send("Invalid input. Duration days should be greater than 0, and eligibility criteria should be non-negative.")
            return

        # Check if an event with the same name already exists
        if event_name in event_data:
            await ctx.send(f"An event with the same name '{event_name}' already exists.")
            return

        # Create and add the event with the specified data
        event_data[event_name] = {
            'format': event_format,
            'duration_days': duration_days,
            'eligibility_criteria': eligibility_criteria,
            'hashtag': event_hashtag,
            'start_time': datetime.datetime.now(),  # Timestamp when the event starts
        }

        await ctx.send(f"Event '{event_name}' created with {event_hashtag} hashtag, format: {event_format}, {duration_days} days duration, and eligibility criteria: {eligibility_criteria}.")
    else:
        await ctx.send("You do not have permission to create events.")







# Function to update the user's streak
streaks = {}

def update_streak(user_id, event_name):
    if user_id not in streaks:
        streaks[user_id] = {event_name: 1}
    else:
        if event_name not in streaks[user_id]:
            streaks[user_id][event_name] = 1
        else:
            streaks[user_id][event_name] += 1

@bot.command()
async def mystreak(ctx, event_name: str):
    user_id = ctx.author.id

    # Check if the user has a streak for the specified event
    if user_id in streaks and event_name in streaks[user_id]:
        await ctx.send(f"Your current streak for #{event_name} is {streaks[user_id][event_name]} days.")
    else:
        await ctx.send(f"You don't have an active streak for #{event_name}.")

@bot.command()
async def eligibility(ctx, event_name: str):
    user_id = ctx.author.id

    # Check if the event exists
    if event_name not in event_data:
        await ctx.send(f"The event '{event_name}' does not exist.")
        return

    # Check if the user has participated in the event for the required number of days
    if user_id in streaks and event_name in streaks[user_id]:
        if streaks[user_id][event_name] >= event_data[event_name]['duration_days']:
            eligible_users_list = [str(user) for user in eligible_users]
            eligible_list_message = "Eligible participants:\n" + "\n".join(eligible_users_list)
            await ctx.send(f"You are eligible for rewards in the #{event_name} event!\n{eligible_list_message}")
        else:
            await ctx.send(f"You are not eligible for rewards in the #{event_name} event yet. Keep posting!")
    else:
        await ctx.send(f"You are not eligible for rewards in the #{event_name} event yet. Keep posting!")





@bot.command()
async def export(ctx, event_name: str):
    # Check if the event exists
    if event_name not in event_data:
        await ctx.send(f"The event '{event_name}' does not exist.")
        return

    # Check if the user is an administrator
    if any(role.name == "Administrator" for role in ctx.author.roles):
        # Create a CSV file with the list of eligible participants and their usernames
        eligible_participants = []

        for user_id in eligible_users:
            user = bot.get_user(user_id)
            if user:
                eligible_participants.append(user.name)  # Use user.name to get the username

        file_name = f"{event_name}_participants.csv"

        with open(file_name, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Username"])  # Change the header to "Username"
            writer.writerows([[username] for username in eligible_participants])  # Store each username in a separate row

        # Send the CSV file in the Discord channel
        with open(file_name, "rb") as file:
            await ctx.send(f"Here is the list of eligible participants for '{event_name}':", file=discord.File(file, file_name))

        # Delete the local CSV file
        os.remove(file_name)
    else:
        await ctx.send("You do not have permission to export participants.")






# Function to get eligible users (You need to implement this function)
def get_eligible_users(event_name):
    eligible_users = []

    # Iterate through all users to check eligibility for the specified event
    for user_id in streaks:
        if is_user_eligible(user_id, event_name):
            eligible_users.append(user_id)

    return eligible_users

def is_user_eligible(user_id, event_name):
    # Check if the user has participated for the required number of days (equal to event duration)
    if user_id in streaks and event_name in streaks[user_id]:
        if streaks[user_id][event_name] >= event_data[event_name]['duration_days']:
            return True
    return False


# Example function to get the count of valid posts for a user
def get_valid_post_count(user_id):
    # Implement logic to retrieve the count of valid posts for the user
    # For example, you can query a database or keep track of it in your bot's data
    # Return the count of valid posts
    pass


# Define a dictionary to store user token balances
user_tokens = {}

@bot.command()
async def distribute_tokens(ctx, event_name: str, amount_per_user: int):
    print(f"Received distribute_tokens command with event_name={event_name}, amount_per_user={amount_per_user}")

    # Check if the user has the necessary permissions (e.g., server administrators)
    if any(role.name == "Administrator" for role in ctx.author.roles):
        print("User has administrator permissions.")
        eligible_users = get_eligible_users(event_name)  # Fetch eligible users for the specified event
        total_users = len(eligible_users)

        print(f"Total eligible users: {total_users}")

        if total_users > 0:
            total_tokens = amount_per_user * total_users  # Total tokens to distribute
            failed_users = []

            for user_id in eligible_users:
                try:
                    # Implement logic to distribute tokens to eligible users
                    # Assuming you have a dictionary 'user_tokens' to store user token balances
                    if user_id in user_tokens:
                        user_tokens[user_id] += amount_per_user  # Add tokens to the user's balance
                    else:
                        user_tokens[user_id] = amount_per_user  # Create a new balance for the user
                except Exception as e:
                    # If an error occurs while distributing tokens to a user, log the error and continue
                    error_message = f"Error distributing tokens to user {user_id}: {str(e)}"
                    print(error_message)
                    await ctx.send(error_message)  # Send an error message to the user
                    failed_users.append(user_id)

            if failed_users:
                await ctx.send(f"{total_tokens} tokens distributed to eligible participants, but there were errors for some users.")
            else:
                await ctx.send(f"{total_tokens} tokens distributed to eligible participants successfully.")
        else:
            await ctx.send("There are no eligible participants for the specified event.")
    else:
        await ctx.send("You do not have permission to distribute tokens.")




reminder_flags = {}  # Dictionary to store reminder flags

@bot.command()
async def remindme(ctx):
    user_id = ctx.author.id

    if user_id not in reminder_flags or not reminder_flags[user_id]:
        reminder_flags[user_id] = True
        await ctx.send("You will receive daily reminders to post.")
        await send_daily_reminder(ctx, user_id)
    else:
        await ctx.send("You are already scheduled to receive reminders.")

@bot.command()
async def noremind(ctx):
    user_id = ctx.author.id

    if user_id in reminder_flags and reminder_flags[user_id]:
        reminder_flags[user_id] = False
        await ctx.send("You will no longer receive daily reminders.")
    else:
        await ctx.send("You don't have any active reminders.")

async def send_daily_reminder(ctx, user_id):
    while reminder_flags.get(user_id, False):
        # Send the reminder message
        await ctx.send("Don't forget to post today!")

        # Wait for 24 hours before sending the next reminder
        await asyncio.sleep(86400)  # 24 hours




# Run the bot with the token stored in the environment variable
bot.run('MTE1NzcwNDU5NDExNDIzMjQ1MQ.GK6Acc.qVulN2xf9o1Et8v0MAarSJgXK5zuzJXx8sTBzw')

