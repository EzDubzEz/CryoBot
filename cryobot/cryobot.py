import discord
from discord.ext import commands, tasks
import aiohttp
from helper import debugPrint, getVariable
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from scrim_classes import Scrim, Team, ScrimFormat, Reputation, CryoBotError
from google_api import GoogleAPI
from gankster import Gankster
from discord_stuff import DiscordStuff
import functools

DISCORD_TOKEN = getVariable("DISCORD_TOKEN")
CHANNEL_ID = getVariable("CHANNEL_ID")
GUILD_ID = getVariable("GUILD_ID")
TREBOTEHTREE = getVariable("TREBOTEHTREE")

class CryoBot:
    def __init__(self):
        self.scrimRequests: list[discord.Message] = []
        self.scrimFounds: list[discord.Message] = []
        self._poll_send_time = time(hour=6, tzinfo=ZoneInfo("America/New_York"))

        self._google_api = GoogleAPI()
        self._gankster = Gankster()

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
                url, headers, payload = DiscordStuff.create_weekly_poll(start, end)

                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            debugPrint("Sucessfully Posted Weekly Poll")
                        else:
                            debugPrint(f"Failed To Post Weekly Poll: {await resp.text()}")

        @tasks.loop(hours=6)
        async def refresh_google_api():
            if refresh_google_api.current_loop == 0:
                return
            debugPrint("Refreshing Google API Token")
            try:
                self._google_api.refreshCreds()
                debugPrint("Google API Token Refreshed Successfully")
            except Exception as e:
                debugPrint(f"Issue in Google API loop: {e}")

        @self._bot.tree.command(name="hello_world2", description="Prints Hello World",  guild=discord.Object(id=GUILD_ID))
        async def hello_world2(interaction: discord.Interaction, number: str):
            debugPrint(f"Attempting to print \"Hello World: {number}\"")
            await interaction.response.send_message(f"Hello World: {number}")


        @self._bot.tree.command(name="one", guild=discord.Object(id=GUILD_ID))
        async def one(interaction: discord.Interaction): # TODO: Make this not a command and be automatic
            scrim = Scrim(datetime.now(), ScrimFormat.THREE_GAMES)
            embed = DiscordStuff.create_looking_for_scrim_embed(scrim)
            
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
            # embed = DiscordStuff.create_scrim_found_embed(scrim)
            embed = DiscordStuff.create_scrcim_request_recieved_embed(scrim)
            await interaction.response.send_message(content="<@&378729316990713856>", embed=embed)
            self.scrimFounds.append(await interaction.original_response())

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        async def four(interaction: discord.Interaction):# TODO: Make this not a command and be automatic
            await self.scrimFounds.pop(0).delete()
            team = Team("84830", "Cryobarkers", "Gold/Platinum", opggLink="https://www.op.gg/multisearch/na?summoners=DiamondPhoenix22%23NA1,Sp6rtan%23666,Superice%2300000,TreboTehTree%23NA1,BenAndM%23NA1")
            scrim = Scrim(datetime.now(), ScrimFormat.THREE_GAMES, team)
            embed = DiscordStuff.create_scrim_cancelled_embed(scrim)

            await interaction.response.send_message(content="<@&378729316990713856>", embed=embed)

        def _handle_error():
            def decorator(func):
                @functools.wraps(func)
                async def wrapper(*args, **kwargs):
                    interaction: discord.Interaction = args[0]
                    try:
                        return await func(*args, **kwargs)
                    except CryoBotError as e:
                        debugPrint(f"CryoBotError performing command {func.__name__}: {e}")
                        try:
                            await interaction.response.send_message(f"Uh Oh <@{TREBOTEHTREE}>, we  ran into an issue: {e}")
                        except discord.InteractionResponded:
                            await interaction.followup.send(f"Uh Oh <@{TREBOTEHTREE}>, we  ran into an issue: {e}")
                    except Exception as e:
                        debugPrint(f"Error performing command {func.__name__}: {e}")
                        try:
                            await interaction.response.send_message(f"I, CryoBot, ran into an issue: {e}")
                        except discord.InteractionResponded:
                            await interaction.followup.send(f"I, CryoBot, ran into an issue: {e}")
                return wrapper
            return decorator
        formats = [
            discord.app_commands.Choice(name="Bo1", value="Bo1"),
            discord.app_commands.Choice(name="Bo2", value="Bo2"),
            discord.app_commands.Choice(name="Bo3", value="Bo3"),
            discord.app_commands.Choice(name="Bo4", value="Bo4"),
            discord.app_commands.Choice(name="Bo5", value="Bo5"),
            discord.app_commands.Choice(name="1 Game", value="1 Game"),
            discord.app_commands.Choice(name="2 Games", value="2 Games"),
            discord.app_commands.Choice(name="3 Games", value="3 Games"),
            discord.app_commands.Choice(name="4 Games", value="4 Games"),
            discord.app_commands.Choice(name="5 Games", value="5 Games")
        ]

        @self._bot.tree.command(name="help", description="Displays list of commands.")
        async def help(interaction: discord.Interaction):
            debugPrint("Attempting to list commands")
            message = "/create_scrim_request [date] [time] [format]\n" \
                            "/cancel_scrim_request [date] [time] [format]\n" \
                            "/cancel_all_scrim_requests\n" \
                            "/accept_scrim_request [team_name] [date] [time] [format]\n" \
                            "/decline_scrim_request [team_name] [date] [time] [format]\n" \
                            "/send_scrim_request [team_name] [date] [time] [format]\n" \
                            "/retrieve_team_number [team_name]\n" \
                            "/retrieve_team_data [team_number]\n" \
                            "/help"

            embed = discord.Embed(
                title="Commands",
                color=discord.Color.dark_gray(),
                description=message
            )
            await interaction.response.send_message(embed=embed)
            debugPrint("Successfully sent command list\n")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.choices(format=formats)
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_error()
        async def create_scrim_request(interaction: discord.Interaction, date: str, time: str, format: str):
            debugPrint(f"Attempting to create scrim request: date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format)) 
            await interaction.response.defer()
            self._gankster.create_scrim_request(scrim)
            debugPrint("Scrim Request Sucessfully Created")
            await interaction.followup.send("Scrim Request Sucessfully Created")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.choices(format=formats)
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_error()
        async def cancel_scrim_request(interaction: discord.Interaction, date: str, time: str,  format: str):
            debugPrint(f"Attempting to cancel scrim request: date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format)) 
            await interaction.response.defer()
            self._gankster.cancel_scrim_request(scrim)
            debugPrint("Scrim Request Sucessfully Cancelled")
            await interaction.followup.send("Scrim Request Sucessfully Cancelled")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_error()
        async def cancel_all_scrim_requests(interaction: discord.Interaction):
            debugPrint("Attempting to cancel all scrim requests")
            await interaction.response.defer()
            self._gankster.cancel_all_scrim_requests()
            debugPrint("All Scrim Requests Sucessfully Cancelled")
            await interaction.followup.send("All Scrim Requests Sucessfully Cancelled")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.choices(format=formats)
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_error()
        async def accept_scrim_request(interaction: discord.Interaction, team_name: str, date: str, time: str,  format: str):
            debugPrint(f"Attempting to accept scrim request: team_name='{team_name}', date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
            team = Team(name=team_name)
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format), team) 
            await interaction.response.defer()
            self._gankster.process_scrim_request(scrim, True)
            debugPrint("Scrim Request Sucessfully Accepted")
            await interaction.followup.send("Scrim Request Sucessfully Accepted")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.choices(format=formats)
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_error()
        async def decline_scrim_request(interaction: discord.Interaction, team_name: str, date: str, time: str,  format: str):
            debugPrint(f"Attempting to decline scrim request: team_name='{team_name}', date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
            team = Team(name=team_name)
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format), team) 
            await interaction.response.defer()
            self._gankster.process_scrim_request(scrim, False)
            debugPrint("Scrim Request Sucessfully Declined")
            await interaction.followup.send("Scrim Request Sucessfully Declined")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.choices(format=formats)
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_error()
        async def send_scrim_request(interaction: discord.Interaction, team_name: str, date: str, time: str,  format: str):
            debugPrint(f"Attempting to send scrim request: team_name='{team_name}', date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
            team = Team(name=team_name)
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format), team) 
            await interaction.response.defer()
            self._gankster.send_scrim_request(scrim)
            debugPrint("Scrim Request Sucessfully Sent")
            await interaction.followup.send("Scrim Request Sucessfully Sent")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_error()
        async def retrieve_team_number(interaction: discord.Interaction, team_name: str):
            debugPrint(f"Attempting to retrieve team number: team_name='{team_name}'")
            await interaction.response.defer()
            number = self._gankster.retrieve_team_number(team_name)
            debugPrint("Team Number Sucessfully Retrieved")
            await interaction.followup.send(f"The Team [{team_name}] has the number {number}")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_error()
        async def retrieve_team_data(interaction: discord.Interaction, team_number: str):
            debugPrint(f"Attempting to retrieve team number: team_number='{team_number}'")
            await interaction.response.defer()
            team = Team(team_number)
            self._gankster.fill_team_stats(team)
            debugPrint("Scrim Request Sucessfully Sent")
            await interaction.followup.send("Scrim Request Sucessfully Sent")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_error()
        async def update_scrim_results_sheet(interaction: discord.Interaction):
            debugPrint(f"Attempting to update scrim results sheet")
            await interaction.response.defer()
            self._google_api.update_scrim_results()
            debugPrint("Sucessfully Updated Scrim Results")
            await interaction.followup.send("Sucessfully Updated Scrim Results")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_error()
        async def reset_scrim_results_sheet_data(interaction: discord.Interaction):
            debugPrint(f"Attempting to reset scrim results sheet data")
            await interaction.response.defer()
            self._google_api.reset_scrim_results_data()
            debugPrint("Sucessfully Reset Scrim Results Data")
            await interaction.followup.send("Sucessfully Reset Scrim Results Data")

if __name__ == "__main__":
    bot = CryoBot()