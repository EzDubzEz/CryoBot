import discord
from discord.ext import commands, tasks
import aiohttp
from helper import debugPrint, getVariable
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from scrim_classes import Scrim, Team, ScrimFormat, Reputation
from google_api import GoogleAPI

DISCORD_TOKEN = getVariable("DISCORD_TOKEN")
CHANNEL_ID = getVariable("CHANNEL_ID")
GUILD_ID = getVariable("GUILD_ID")

class CryoBot:
    def __init__(self):
        self.scrimRequests: list[discord.Message] = []
        self.scrimFounds: list[discord.Message] = []
        self._poll_send_time = time(hour=6, tzinfo=ZoneInfo("America/New_York"))

        self._google_api = GoogleAPI()

        intents = discord.Intents.none()
        intents.guilds = True
        intents.messages = True

        self._bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
        
        self._register_commands()

        self._bot.run(DISCORD_TOKEN)

        
    
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
                post_weekly_poll.start()
                debugPrint(f"Starting repeating poll")
            except Exception as e:
                debugPrint(f"Failed to start poll loop: {e}")
            try:
                refresh_google_api.start()
                debugPrint(f"Starting repeating Google API refresh")
            except Exception as e:
                debugPrint(f"Failed to start Google API refresh loop: {e}")
        
        @tasks.loop(time=self._poll_send_time)
        async def post_weekly_poll():
            now = datetime.now(ZoneInfo("America/New_York"))
            if now.weekday() == 5:
                start = (now + timedelta(days=2)).strftime("%d/%m")
                end = (now + timedelta(days=8)).strftime("%d/%m")
                HEADERS = {
                    "Authorization": f"Bot {DISCORD_TOKEN}",
                    "Content-Type": "application/json"
                }

                url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

                payload = {
                    "poll": {
                        "question": {"text": f"📅 Scrim Availability {start} - {end}"},
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
                        if resp.status == 200:
                            debugPrint("Sucessfully Posted Weekly Poll")
                        else:
                            debugPrint(f"Failed To Post Weekly Poll: {await resp.text()}")

        @tasks.loop(hours=6)
        async def refresh_google_api():
            debugPrint("Refreshing Google API Token")
            if refresh_google_api.current_loop == 0:
                return
            debugPrint("Refreshing Google API Token2")
            try:
                self._google_api.refreshCreds()
            except Exception as e:
                debugPrint(f"Issue in Google API loop: {e}")

        @self._bot.tree.command(name="hello_world2", description="Prints Hello World",  guild=discord.Object(id=GUILD_ID))
        async def hello_world2(interaction: discord.Interaction, number: str):
            debugPrint(f"Attempting to print \"Hello World: {number}\"")
            await interaction.response.send_message(f"Hello World: {number}")


        @self._bot.tree.command(name="one", guild=discord.Object(id=GUILD_ID))
        async def one(interaction: discord.Interaction): # TODO: Make this not a command and be automatic
            scrim = Scrim(datetime.now(), ScrimFormat.THREE_GAMES)
            embed = self._create_looking_for_scrim_embed(scrim)
            
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
            rep = Reputation("4.79")
            team = Team("84830", "Cryobarkers", "Gold/Platinum", opggLink="https://www.op.gg/multisearch/na?summoners=DiamondPhoenix22%23NA1,Sp6rtan%23666,Superice%2300000,TreboTehTree%23NA1,BenAndM%23NA1", reputation=rep)
            scrim = Scrim(datetime.now(), ScrimFormat.THREE_GAMES, team)
            embed = self._create_scrim_found_embed(scrim)
            await interaction.response.send_message(content="<@&378729316990713856>", embed=embed)
            self.scrimFounds.append(await interaction.original_response())

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        async def four(interaction: discord.Interaction):# TODO: Make this not a command and be automatic
            await self.scrimFounds.pop(0).delete()
            team = Team("84830", "Cryobarkers", "Gold/Platinum", opggLink="https://www.op.gg/multisearch/na?summoners=DiamondPhoenix22%23NA1,Sp6rtan%23666,Superice%2300000,TreboTehTree%23NA1,BenAndM%23NA1")
            scrim = Scrim(datetime.now(), ScrimFormat.THREE_GAMES, team)
            embed = self._create_scrim_cancelled_embed(scrim)

            await interaction.response.send_message(content="<@&378729316990713856>", embed=embed)

            # embed.set_footer(text="Gankster Scrim Bot • Cryobark Ops")
            # embed.set_thumbnail(url="https://example.com/cancel_icon.png")

    def _create_looking_for_scrim_embed(self, scrim: Scrim) -> discord.Embed:
        embed = discord.Embed(
            title="Scrim Request Sent",
            description="Cryobark has sent out a request for a scrim!",
            color=discord.Color.gold()
        )
        dateString = scrim.time.strftime("%A, %B %d")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrimFormat.format, inline=True)
        embed.set_footer(text="Awaiting opponent...")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Enemy_Missing_ping.png")

        return embed

    def _create_scrim_found_embed(self, scrim: Scrim) -> discord.Embed:
        embed = discord.Embed(
            title=f"Scrim Found vs {scrim.team.name}",
            description="Get ready to rumble!",
            color=discord.Color.blue(),
            url=f"https://lol.gankster.gg/teams/{scrim.team.number}"
        )

        dateString = scrim.time.strftime("%A, %B %d")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrimFormat.format, inline=True)

        rep = ""
        if scrim.team.reputation:
            rep = scrim.team.reputation.gankRep
        embed.add_field(name="Team", value=scrim.team.name, inline=True)
        embed.add_field(name="Rank", value=scrim.team.rank, inline=True)
        embed.add_field(name="GankRep", value=rep, inline=True)

        embed.set_author(name="OP.GG", url=scrim.team.opggLink)
        # embed.set_footer(text="Awaiting opponent...")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/On_My_Way_ping.png") #I updated this on the wiki so I could use the correct looking one :D

        return embed

    def _create_scrim_cancelled_embed(self, scrim: Scrim) -> discord.Embed:
        embed = discord.Embed(
            title=f"Scrim Canceled vs {scrim.team.name}",
            description=f"Darn {scrim.team.name} how unreliable!",
            color=discord.Color.red()
        )

        dateString = scrim.time.strftime("%A, %B %d")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrimFormat.format, inline=True)

        # rep = ""
        # if scrim.team.reputation:
        #     rep = scrim.team.reputation.gankRep
        # embed.add_field(name="Team", value=scrim.team.name, inline=True)
        # embed.add_field(name="Rank", value=scrim.team.rank, inline=True)
        # embed.add_field(name="GankRep", value=rep, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Retreat_ping.png")

        return embed




    

        


if __name__ == "__main__":
    bot = CryoBot()