import discord
from discord.ext import commands, tasks
import aiohttp
from helper import debugPrint, getVariable
import datetime
from zoneinfo import ZoneInfo

DISCORD_TOKEN = getVariable("DISCORD_TOKEN")
CHANNEL_ID = getVariable("CHANNEL_ID")
GUILD_ID = getVariable("GUILD_ID")
PollSend = datetime.time(hour=6, tzinfo=ZoneInfo("America/New_York"))

class CryoBot:
    def __init__(self):
        self.scrimRequests: list[discord.Message] = []
        self.scrimFounds: list[discord.Message] = []
        intents = discord.Intents.none()
        intents.guilds = True
        intents.messages = True

        self._bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
        
        self._register_commands()

        self._bot.run(DISCORD_TOKEN)
        try:
            self.post_native_poll.start()
            debugPrint(f"Starting repeating tracker")
        except Exception as e:
            debugPrint(f"Failed to start loop: {e}")

        
    
    def _register_commands(self):
        @self._bot.event
        async def on_ready():
            debugPrint(f"Logged in as {self._bot.user} (ID: {self._bot.user.id})")
            try:
                synced = await self._bot.tree.sync(guild=discord.Object(id=GUILD_ID))
                debugPrint(f"Synced {len(synced)} slash commands")
            except Exception as e:
                debugPrint(f"Failed to sync commands: {e}")
            try:
                # my_repeating_task.start()
                debugPrint(f"Starting repeating tracker")
            except Exception as e:
                debugPrint(f"Failed to start loop: {e}")

        @self._bot.tree.command(name="hello_world2", description="Prints Hello World",  guild=discord.Object(id=GUILD_ID))
        async def hello_world2(interaction: discord.Interaction, number: str):
            debugPrint(f"Attempting to print \"Hello World: {number}\"")
            await interaction.response.send_message(f"Hello World: {number}")


        @self._bot.tree.command(name="one", guild=discord.Object(id=GUILD_ID))
        async def one(interaction: discord.Interaction): # TODO: Make this not a command and be automatic
            embed = discord.Embed(
                title="Scrim Request Sent",
                description="Cryobark has sent out a request for a scrim!",
                color=discord.Color.gold()
            )

            embed.add_field(name="Date", value="Saturday, June 15", inline=True)
            embed.add_field(name="Time", value="9:00 PM EST", inline=True)
            embed.add_field(name="Format", value="3 Games", inline=True)
            embed.set_footer(text="Awaiting opponent...")

            embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Enemy_Missing_ping.png")
            
            await interaction.response.send_message(embed=embed)
            self.scrimRequests.append(await interaction.original_response())

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        async def two(interaction: discord.Interaction):# TODO: Make this not a command and be automatic
            for message in self.scrimRequests:
                await message.delete()
            self.scrimRequests = []
            for message in self.scrimFounds:
                await message.delete()
            self.scrimFounds = []
            await interaction.response.send_message("done")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        async def three(interaction: discord.Interaction):# TODO: Make this not a command and be automatic
            await self.scrimRequests.pop(0).delete()
            embed = discord.Embed(
                title="Scrim Found vs Cryobarkers",
                description="Get ready to rumble!",
                color=discord.Color.blue(),
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

            embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/On_My_Way_ping_Updated.png") #I updated this on the wiki so I could use the correct looking one :D
            await interaction.response.send_message(content="<@&378729316990713856>", embed=embed)
            self.scrimFounds.append(await interaction.original_response())

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        async def four(interaction: discord.Interaction):# TODO: Make this not a command and be automatic
            await self.scrimFounds.pop(0).delete()
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
            
            embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Retreat_ping.png")

            await interaction.response.send_message(content="<@&378729316990713856>", embed=embed)

            # embed.set_footer(text="Gankster Scrim Bot • Cryobark Ops")
            # embed.set_thumbnail(url="https://example.com/cancel_icon.png")



    @tasks.loop(time=PollSend)
    async def post_native_poll(self):
        time = datetime.now(ZoneInfo("America/New_York"))
        if datetime.datetime.today().weekday() == 5:
            HEADERS = {
                "Authorization": f"Bot {DISCORD_TOKEN}",
                "Content-Type": "application/json"
            }

            url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

            payload = {
                "poll": {
                    "question": {"text": "📅 Scrim Availability"},
                    "answers": [
                        {"poll_media": {"text": "Monday"}},
                        {"poll_media": {"text": "Tuesday"}},
                        {"poll_media": {"text": "Wednesday"}},
                        {"poll_media": {"text": "Thursday"}},
                        {"poll_media": {"text": "Friday"}},
                        {"poll_media": {"text": "Saturday"}},
                        {"poll_media": {"text": "Sunday"}}
                    ],
                    "allow_multiselect": True,
                    "duration": 48  # in Hours 
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=HEADERS, json=payload) as resp:
                    print("Status:", resp.status)
                    print("Response:", await resp.text())

        


if __name__ == "__main__":
    bot = CryoBot()