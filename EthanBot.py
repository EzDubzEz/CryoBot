import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
PUBLIC_KEY = os.getenv("PUBLIC_KEY")
DEBUG_MODE = os.getenv("DEBUG_MODE") == "True"

def debugPrint(text):
    if DEBUG_MODE:
        print(text)

intents = discord.Intents.none()
intents.guilds = True
intents.messages = True

bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)

@bot.event
async def on_ready():
    debugPrint(f"Logged in as {bot.user} (ID: {bot.user.id})")
    try:
        synced = await bot.tree.sync()
        debugPrint(f"Synced {len(synced)} slash commands")
    except Exception as e:
        debugPrint(f"Failed to sync commands: {e}")
    try:
        # my_repeating_task.start()
        debugPrint(f"Starting repeating tracker")
    except Exception as e:
        debugPrint(f"Failed to start loop: {e}")

@bot.tree.command(name="helloworld", description="Prints Hello World")
async def add_account(interaction: discord.Interaction, number: str):
    debugPrint(f"Attempting to print \"Hello World: {number}\"")
    await interaction.response.send_message(f"Hello World: {number}")

scrimRequests = []
scrimFounds = []
@bot.command()
async def one(ctx): # TODO: Make this not a command and be automatic
    embed = discord.Embed(
        title="Scrim Request Sent",
        description="Cryobark has sent out a request for a scrim!",
        color=discord.Color.gold()
    )

    embed.add_field(name="Date", value="Saturday, June 15", inline=True)
    embed.add_field(name="Time", value="9:00 PM EST", inline=True)
    embed.add_field(name="Format", value="3 Games", inline=True)
    embed.set_footer(text="Awaiting opponent...")

    embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Enemy_Missing_ping.png?4ebe8")
    scrimRequests.append(await ctx.send(embed=embed))

@bot.command()
async def two(ctx):# TODO: Make this not a command and be automatic
    for message in scrimRequests:
        await message.delete()
    for message in scrimFounds:
        await message.delete()

@bot.command()
async def three(ctx):# TODO: Make this not a command and be automatic
    await scrimRequests[0].delete()
    embed = discord.Embed(
        title="Scrim Found vs Cryobarkers",
        description="Get ready to rumble!",
        color=discord.Color.gold(),
        url="https://lol.gankster.gg/teams/84830/cryobark"
    )

    embed.add_field(name="Date", value="Saturday, June 15", inline=True)
    embed.add_field(name="Time", value="9:00 PM EST", inline=True)
    embed.add_field(name="Format", value="3 Games", inline=True)
    
    embed.add_field(name="Team", value="Cryobarkers", inline=True)
    embed.add_field(name="Rank", value="Gold/Platinum", inline=True)
    embed.add_field(name="GankRep", value="4.99", inline=True)

    embed.set_author(name="OP.GG", url="https://op.gg/lol/summoners/na/TreboTehTree-NA1")
    # embed.set_footer(text="Awaiting opponent...")

    embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/All_In_ping.png?0f8e9")
    scrimFounds.append(await ctx.send(content="<@&378729316990713856>", embed=embed))

@bot.command()
async def four(ctx):# TODO: Make this not a command and be automatic
    await scrimFounds[0].delete()
    embed = discord.Embed(
        title="Scrim Canceled vs Cryobarkers",
        description="Darn Cryobarkers how unreliable!",
        color=discord.Color.red()
    )

    embed.add_field(name="Date", value="Saturday, June 15", inline=True)
    embed.add_field(name="Time", value="9:00 PM EST", inline=True)
    embed.add_field(name="Format", value="3 Games", inline=True)
    
    embed.add_field(name="Team", value="Cryobarkers", inline=True)
    embed.add_field(name="Rank", value="Gold/Platinum", inline=True)
    embed.add_field(name="GankRep", value="4.99", inline=True)
    
    embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Retreat_ping.png?5abe9")

    await ctx.send(content="<@&378729316990713856>", embed=embed)

    # embed.set_footer(text="Gankster Scrim Bot • Cryobark Ops")
    # embed.set_thumbnail(url="https://example.com/cancel_icon.png")