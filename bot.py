import discord
from discord.ext import commands
import os  # Import the os module to access environment variables


intents = discord.Intents.default()
intents.typing = False
intents.presences = False

bot = commands.Bot(command_prefix='!', intents=intents)

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
        # Update the user's streak (You'll need to implement this)
        # For now, let's assume there's a function to update the streak
        update_streak(ctx.author.id)
        await ctx.send("Your daily post for the #30DaysOfCode challenge has been counted!")
    else:
        await ctx.send("Please include the #30DaysOfCode hashtag in your post to count it.")

# Function to update the user's streak (You can implement this logic)
def update_streak(user_id):
    # Implement logic to update the user's streak in your database or data structure
    pass


# Run the bot with the token stored in the environment variable
bot.run('MTE1NzcwNDU5NDExNDIzMjQ1MQ.GaCqPw.SezY_UHVLARK0gEHOqCXQtHY3VZJT53Ibs_Lek')

