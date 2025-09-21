import functools
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

import discord
from discord.ext import commands, tasks

from gankster import Gankster
from google_api import GoogleAPI
from helper import debugPrint, getVariable, setVariable
from scrim_classes import CryoBotError, Scrim, ScrimFormat, Team
from discord_stuff import DiscordStuff

DISCORD_TOKEN: str = getVariable("DISCORD_TOKEN")
POLL_CHANNEL_ID: int = getVariable("POLL_CHANNEL_ID")
SCRIM_CHANNEL_ID: int = getVariable("SCRIM_CHANNEL_ID")
ERROR_CHANNEL_ID: int = getVariable("ERROR_CHANNEL_ID")
GUILD_ID: int = getVariable("GUILD_ID")
TREBOTEHTREE: int = getVariable("TREBOTEHTREE")
CRYOBARK_ROLE_ID: int = getVariable("CRYOBARK_ROLE_ID")
MANAGER_ROLE_ID: int = getVariable("MANAGER_ROLE_ID")
POLL_PINGERS: list[int] = getVariable("POLL_PINGERS")
ALL_MEMBERS: set[int] = getVariable("ALL_MEMBERS")
CRYOBARK: Team = getVariable("CRYOBARK")
WILDCARD_TEAM: Team = getVariable("WILDCARD_TEAM")

class CryoBot:
    def __init__(self):
        self._guild: discord.Guild
        self._poll_channel: discord.TextChannel
        self._scrim_channel: discord.TextChannel
        self._error_channel: discord.TextChannel

        self._latest_poll_message: discord.InteractionMessage
        self._poll_voters: set[int] = set()

        self._incoming_scrim_request_messages: list[tuple[Scrim, discord.Message]] = []
        self._outgoing_scrim_request_messages: list[tuple[Scrim, discord.Message]] = []
        self._current_scrims: set[Scrim] = set()
        self._scrim_messages: dict[Scrim, discord.Message] = {}
        self._played_scrims: set[Scrim] = set()

        debugPrint("Starting Google API")
        self._google_api = GoogleAPI()
        debugPrint("Starting Gankster")
        self._gankster = Gankster()

        intents = discord.Intents.none()
        intents.guilds = True
        intents.messages = True
        intents.polls = True
        intents.members = True
        self.flag = True

        self._bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents,)

        self._register_commands()

        self._bot.run(DISCORD_TOKEN)

    def _register_commands(self):
        @self._bot.event
        async def on_ready():
            debugPrint(f"Logged in as {self._bot.user} (ID: {self._bot.user.id})")
            self._guild = self._bot.get_guild(GUILD_ID)
            self._poll_channel = self._bot.get_channel(POLL_CHANNEL_ID)
            self._scrim_channel = self._bot.get_channel(SCRIM_CHANNEL_ID)
            self._error_channel = self._bot.get_channel(ERROR_CHANNEL_ID)
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
            try:
                update_scrim_status.start()
                debugPrint(f"Starting repeating updating scrim status loop")
            except Exception as e:
                debugPrint(f"Failed to start repeating updating scrim status loop: {e}")
            try:
                refresh_gankster_token.start()
                debugPrint(f"Starting repeating refresh gankster token loop")
            except Exception as e:
                debugPrint(f"Failed to start repeating refresh gankster token loop: {e}")
            await self._gankster.fill_team_stats(CRYOBARK)

        @tasks.loop(time=time(hour=4, tzinfo=ZoneInfo("America/New_York")))
        async def post_weekly_poll():
            now = datetime.now(ZoneInfo("America/New_York"))
            if now.weekday() == 4: # Friday
                try:
                    debugPrint("Attempting To Post Weekly Poll")
                    self._poll_voters = set()
                    start = (now + timedelta(days=3)).strftime("%m/%d")
                    end = (now + timedelta(days=9)).strftime("%m/%d")
                    poll = DiscordStuff.create_weekly_poll(start, end)
                    self._latest_poll_message = await self._poll_channel.send(poll=poll)
                    debugPrint("Sucessfully Posted Weekly Poll")
                except Exception as e:
                    debugPrint(f"Failed To Post Weekly Poll: {e}")
            if now.weekday() == 5 and self._latest_poll_message != None: # Saturday
                try:
                    debugPrint("Attempting To Post Poll Reminder")
                    self._latest_poll_message = await self._latest_poll_message.fetch()

                    poll_ping_people = ', '.join([f"<@{person}>" for person in POLL_PINGERS if person not in self._poll_voters])
                    if poll_ping_people:
                        await self._poll_channel.send(f"{poll_ping_people} please remember to vote in the poll")
                    else:
                        if self._poll_voters == ALL_MEMBERS:
                            await self._latest_poll_message.poll.end()
                    debugPrint("Sucessfully Posted Poll Reminder")
                except Exception as e:
                    debugPrint(f"Failed To Post Poll Reminder: {e}")

        @self._bot.event
        async def on_poll_vote_add(user: discord.Member, answer):
            debugPrint(f"Adding Poll Vote: user={user}, answer={answer}")
            self._poll_voters.add(user.id)

        @tasks.loop(hours=6)
        async def refresh_google_api():
            if refresh_google_api.current_loop == 0:
                return
            debugPrint("Refreshing Google API Token")
            try:
                await self._google_api.refresh_token()
                debugPrint("Google API Token Refreshed Successfully")
            except Exception as e:
                debugPrint(f"Issue in Google API loop: {e}")

        async def handle_incoming_scrim_requests():
            incoming_scrim_requests = await self._gankster.retrieve_incoming_scrim_requests()

            # For every exting scrim request check if still present, if not remove it
            for scrim_request, _ in self._incoming_scrim_request_messages.copy():
                found = False
                for i in range(len(incoming_scrim_requests)):
                    if scrim_request.equals_exact(incoming_scrim_requests[i]):
                        found = True
                        break
                if not found:
                    await self._incoming_scrim_request_removed(scrim_request)

            # For every new scrim request check if not already present, if so add it
            for scrim_request in incoming_scrim_requests:
                found = False
                for i in range(len(self._incoming_scrim_request_messages)):
                    if scrim_request.equals_exact(self._incoming_scrim_request_messages[i][0]):
                        found = True
                        break
                if not found:
                    await self._incoming_scrim_request_recieved(scrim_request)

        async def handle_outgoing_scrim_requests():
            outgoing_scrim_requests = await self._gankster.retrieve_outgoing_scrim_requests()

            # For every exting scrim request check if still present, if not remove it
            for scrim_request, _ in self._outgoing_scrim_request_messages.copy():
                found = False
                for i in range(len(outgoing_scrim_requests)):
                    if scrim_request.equals_exact(outgoing_scrim_requests[i]):
                        found = True
                        break
                if not found:
                    await self._outgoing_scrim_request_removed(scrim_request)

            # For every new scrim request check if not already present, if so add it
            for scrim_request in outgoing_scrim_requests:
                found = False
                for i in range(len(self._outgoing_scrim_request_messages)):
                    if scrim_request.equals_exact(self._outgoing_scrim_request_messages[i][0]):
                        found = True
                        break
                if not found:
                    await self._outgoing_scrim_request_recieved(scrim_request)

        async def handle_cryobark_scrims():
            # Manually tested each possible scenario and it works, might add actual comments one day who knows
            now = datetime.now()
            for scrim in self._current_scrims.copy():
                if scrim.get_gankster_removal_time() < now:
                    if not scrim.open:
                        self._current_scrims.pop(scrim)
                        self._played_scrims.add(scrim)
                    else:
                        await self._scrim_request_passed(scrim)

            for scrim in self._played_scrims.copy():
                if scrim.get_scrim_end_time() < now:
                    self._played_scrims.pop(scrim)
                    await self._scrim_played(scrim)

            new_scrims = await self._gankster.retrieve_outgoing_scrims(CRYOBARK)
            for new_scrim in new_scrims:
                if new_scrim in self._current_scrims:
                    for old_scrim in self._current_scrims:
                        if new_scrim == old_scrim:
                            break
                    if new_scrim.open != old_scrim.open:
                        self._current_scrims.remove(old_scrim)
                        self._current_scrims.add(new_scrim)
                        if new_scrim.open:
                            await self._scrim_request_found_cancelled(old_scrim) # GUD
                            await self._scrim_request_resent(new_scrim) # GUD
                        else:
                            if new_scrim.team == WILDCARD_TEAM:
                                await self._scrim_request_wildcard_booked(new_scrim) # GUD
                            else:
                                await self._scrim_request_booked(new_scrim) # GUD
                    elif new_scrim.team != old_scrim.team:
                        self._current_scrims.remove(old_scrim)
                        self._current_scrims.add(new_scrim)
                        if old_scrim.team == WILDCARD_TEAM:
                            await self._scrim_request_booked(new_scrim) # GUD
                        else:
                            await self._scrim_request_found_cancelled(old_scrim) # GUD
                            await self._scrim_request_booked(new_scrim) # GUD
                else:
                    updated = False
                    for old_scrim in self._current_scrims:
                        if new_scrim.time == old_scrim.time and old_scrim not in new_scrims:
                            updated = True
                            break
                    if updated:
                        if new_scrim.team == WILDCARD_TEAM and old_scrim.team:
                            new_scrim.team = old_scrim.team
                        self._current_scrims.remove(old_scrim)
                        self._current_scrims.add(new_scrim)
                        if (new_scrim.team == old_scrim.team or old_scrim.team == WILDCARD_TEAM) and new_scrim.team:
                            if new_scrim.team == WILDCARD_TEAM:
                                await self._scrim_request_wildcard_booked_updated(new_scrim, old_scrim) # GUD
                            else:
                                await self._scrim_request_booked_updated(new_scrim, old_scrim) # GUD
                        else:
                            # Team: None/None, TeamA/None, None/TeamB
                            # Open: True/True,   False/True,   True/False
                            if new_scrim.open and old_scrim.open:
                                await self._scrim_request_updated(new_scrim, old_scrim) # GUD
                            elif new_scrim.open and not old_scrim.open:
                                await self._scrim_request_found_cancelled(old_scrim) # GUD
                                await self._scrim_request_resent(new_scrim) # GUD
                            else:
                                if new_scrim.team == WILDCARD_TEAM:
                                    await self._scrim_request_wildcard_updated_booked(new_scrim, old_scrim)
                                else:
                                    await self._scrim_request_updated_booked(new_scrim, old_scrim) # GUD
                    else:
                        # scrim request created
                        self._current_scrims.add(new_scrim)
                        if new_scrim.open:
                            await self._scrim_request_created(new_scrim)  # GUD
                        else:
                            if new_scrim.team == WILDCARD_TEAM:
                                await self._scrim_request_wildcard_booked(new_scrim) # GUD
                            else:
                                await self._scrim_request_booked(new_scrim) # GUD
                        pass

            for scrim in self._current_scrims.copy():
                if scrim not in new_scrims:
                    self._current_scrims.remove(scrim)
                    await self._scrim_request_created_cancelled(scrim) # GUD

        @tasks.loop(minutes=1)
        async def update_scrim_status():
            debugPrint("Starting Update Scrim Status")
            try:
                debugPrint("Starting Handle Incoming Scrim Requests")
                await handle_incoming_scrim_requests()
                debugPrint("Successfulyl Handle Incoming Scrim Requests")
            except Exception as e: debugPrint(f"Failed To Handle Incoming Scrim Requests: {e}")
            try:
                debugPrint("Starting Handle Outgoing Scrim Requests")
                await handle_outgoing_scrim_requests()
                debugPrint("Successfulyl Handle Outgoing Scrim Requests")
            except Exception as e: debugPrint(f"Failed To Handle Outgoing Scrim Requests: {e}")
            try:
                debugPrint("Starting Handle Cryobark Scrims")
                await handle_cryobark_scrims()
                debugPrint("Successfulyl Handle Cryobark Scrims")
            except Exception as e: debugPrint(f"Failed To Handle Cryobark Scrims: {e}")
            debugPrint("Update Scrim Status 'Successful'")

        @tasks.loop(minutes=45)
        async def refresh_gankster_token():
            debugPrint("Refreshing Gankster Token")
            try: 
                await self._gankster.refresh()
                debugPrint("Refreshing Gankster Token Successful")
            except: debugPrint("Failed to Refresh Gankster Token")

        def _handle_interaction_error(func):
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
                            "/cancel_scrim_request [date] [time]\n" \
                            "/cancel_scrim_block [date] [time] [cancellation_msg]\n" \
                            "/accept_scrim_request [team_name] [date] [time] [format]\n" \
                            "/decline_scrim_request [team_name] [date] [time] [format]\n" \
                            "/send_scrim_request [team_name] [date] [time] [format]\n" \
                            "/retrieve_team_data [team_number] [team_name]\n" \
                            "/update_team_players [team_number] [team_name]\n"\
                            "/change_automatic_google [enable_or_disable]\n"\
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
        @_handle_interaction_error
        async def create_scrim_request(interaction: discord.Interaction, date: str, time: str, format: str):
            debugPrint(f"Attempting to create scrim request: date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
                return
            if scrimTime < datetime.now():
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims must be in the future")
                return
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format)) 
            await interaction.response.defer()
            await self._gankster.create_scrim_request(scrim)
            debugPrint("Scrim Request Sucessfully Created")
            await interaction.followup.send("Scrim Request Sucessfully Created")
            await update_scrim_status()

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_interaction_error
        async def cancel_scrim_request(interaction: discord.Interaction, date: str, time: str):
            debugPrint(f"Attempting to cancel scrim request: date='{date}', time='{time}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
                return
            scrim = Scrim(scrimTime)
            await interaction.response.defer()
            await self._gankster.cancel_scrim_request(scrim)
            debugPrint("Scrim Request Sucessfully Cancelled")
            await interaction.followup.send("Scrim Request Sucessfully Cancelled")
            await update_scrim_status()

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_interaction_error
        async def cancel_scrim_block(interaction: discord.Interaction, date: str, time: str, team_name: str, cancellation_msg: str):
            debugPrint(f"Attempting to cancel scrim block: date='{date}', time='{time}', team_name='{team_name}', cancellation_msg='{cancellation_msg}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
                return
            scrim = Scrim(scrimTime, team=Team(name=team_name))
            await interaction.response.defer()
            await self._gankster.cancel_scrim_block(scrim, cancellation_msg)
            debugPrint("Scrim Block Sucessfully Cancelled")
            await interaction.followup.send("Scrim Block Sucessfully Cancelled")
            await update_scrim_status()

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.choices(format=formats)
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_interaction_error
        async def accept_scrim_request(interaction: discord.Interaction, team_name: str, date: str, time: str,  format: str):
            debugPrint(f"Attempting to accept scrim request: team_name='{team_name}', date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
                return
            team = Team(name=team_name)
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format), team) 
            await interaction.response.defer()
            await self._gankster.process_scrim_request(scrim, True)
            debugPrint("Scrim Request Sucessfully Accepted")
            await interaction.followup.send("Scrim Request Sucessfully Accepted")
            await update_scrim_status()

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.choices(format=formats)
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_interaction_error
        async def decline_scrim_request(interaction: discord.Interaction, team_name: str, date: str, time: str,  format: str):
            debugPrint(f"Attempting to decline scrim request: team_name='{team_name}', date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
                return
            team = Team(name=team_name)
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format), team) 
            await interaction.response.defer()
            await self._gankster.process_scrim_request(scrim, False)
            debugPrint("Scrim Request Sucessfully Declined")
            await interaction.followup.send("Scrim Request Sucessfully Declined")
            await update_scrim_status()

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @discord.app_commands.choices(format=formats)
        @discord.app_commands.describe(date = "mm/dd/yy", time="hh:mm AM|PM")
        @_handle_interaction_error
        async def send_scrim_request(interaction: discord.Interaction, team_name: str, date: str, time: str,  format: str):
            debugPrint(f"Attempting to send scrim request: team_name='{team_name}', date='{date}', time='{time}', format='{format}'")
            scrimTime = datetime.strptime(f"{date} {time}", "%m/%d/%y %I:%M %p")
            if scrimTime.minute != 0 and scrimTime.minute != 30:
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims can only be scheduled in 30 minute intervals")
                return
            if scrimTime < datetime.now():
                debugPrint("Invalid Time Format Recieved")
                await interaction.response.send_message("Scrims must be in the future")
                return
            team = Team(name=team_name)
            scrim = Scrim(scrimTime, ScrimFormat.from_short(format), team) 
            await interaction.response.defer()
            await self._gankster.send_scrim_request(scrim)
            debugPrint("Scrim Request Sucessfully Sent")
            await interaction.followup.send("Scrim Request Sucessfully Sent")
            await update_scrim_status()

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_interaction_error
        async def retrieve_team_data(interaction: discord.Interaction, team_number: int=0, team_name: str=""):
            debugPrint(f"Attempting to retrieve team data: team_number={team_number}, team_name='{team_name}'")
            if not team_number and not team_name:
                debugPrint("Invalid Team Format Recieved")
                await interaction.response.send_message("Team Number or Team Name must not be blank")
                return
            await interaction.response.defer()
            team = Team(team_number, team_name)
            await self._gankster.fill_team_stats(team)
            debugPrint("Team Data Sucessfully Retrieved")
            embed = DiscordStuff.create_team_data_embed(team)
            await interaction.followup.send(embed=embed)

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_interaction_error
        async def update_team_players(interaction: discord.Interaction, team_number: int=0, team_name: str=""):
            debugPrint(f"Attempting to update team players: team_number={team_number}, team_name='{team_name}'")
            if not team_number and not team_name:
                debugPrint("Invalid Team Format Recieved")
                await interaction.response.send_message("Team Number or Team Name must not be blank")
                return
            await interaction.response.defer()
            team = Team(team_number, team_name)
            await self._gankster.update_team_players(team)
            debugPrint("Team Players Sucessfully Updated")
            embed = DiscordStuff.create_team_data_embed(team)
            await interaction.followup.send(embed=embed)

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_interaction_error
        async def update_scrim_results_sheet(interaction: discord.Interaction):
            debugPrint(f"Attempting to update scrim results sheet")
            await interaction.response.defer()
            await self._google_api.update_scrim_results()
            debugPrint("Sucessfully Updated Scrim Results")
            await interaction.followup.send("Sucessfully Updated Scrim Results")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_interaction_error
        async def reset_scrim_results_sheet_data(interaction: discord.Interaction):
            debugPrint(f"Attempting to reset scrim results sheet data")
            await interaction.response.defer()  
            await self._google_api.reset_scrim_results_data()
            debugPrint("Sucessfully Reset Scrim Results Data")
            await interaction.followup.send("Sucessfully Reset Scrim Results Data")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_interaction_error
        async def reset_scouting_scrim_results(interaction: discord.Interaction):
            debugPrint(f"Attempting to reset scouting scrim results")
            await interaction.response.defer()  
            await self._google_api.reset_scouting_scrim_results()
            debugPrint("Sucessfully Reset Scouting Scrim Results")
            await interaction.followup.send("Sucessfully Reset Scouting Scrim Results")

        @self._bot.tree.command(guild=discord.Object(id=GUILD_ID))
        @_handle_interaction_error
        async def change_automatic_google(interaction: discord.Interaction, enable_or_disable: bool):
            debugPrint(f"Attempting to change automatic google")
            await interaction.response.defer()  
            setVariable("AUTOMATIC_GOOGLE", enable_or_disable)
            debugPrint("Sucessfully Reset Scouting Scrim Results")
            await interaction.followup.send("Sucessfully Reset Scouting Scrim Results")

    def _handle_automatic_error(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except CryoBotError as e:
                self: CryoBot = args[0]  # kinda skuffed but it works
                debugPrint(f"CryoBotError performing command {func.__name__}: {e}")
                await self._error_channel.send(f"Uh Oh <@{TREBOTEHTREE}>, we ran into an issue: {e}")
            except Exception as e:
                self = args[0]
                debugPrint(f"Error performing command {func.__name__}: {e}")
                await self._error_channel.send(f"Uh Oh <@{TREBOTEHTREE}>, I ran into an issue: {e}")
        return wrapper

    @_handle_automatic_error
    async def _scrim_request_created(self, scrim: Scrim):
        if scrim in  self._scrim_messages:
            await self._scrim_messages[scrim].delete()

        embed = DiscordStuff.create_scrim_request_created_embed(scrim)
        self._scrim_messages[scrim] = await self._scrim_channel.send(f"<@&{MANAGER_ROLE_ID}>", embed=embed)

    @_handle_automatic_error
    async def _scrim_request_booked(self, scrim: Scrim):
        if scrim in self._scrim_messages:
            await self._scrim_messages[scrim].delete()

        embed =DiscordStuff.create_scrim_request_booked_embed(scrim)
        self._scrim_messages[scrim] = await self._scrim_channel.send(f"<@&{CRYOBARK_ROLE_ID}>", embed=embed)

        await self._google_api.found_scrim(scrim)

    @_handle_automatic_error
    async def _scrim_request_found_cancelled(self, scrim: Scrim):
        if scrim in self._scrim_messages:
            await self._scrim_messages[scrim].delete()
            self._scrim_messages.pop(scrim)

        embed = DiscordStuff.create_scrim_request_found_cancelled_embed(scrim)
        await self._scrim_channel.send(f"<@&{CRYOBARK_ROLE_ID}>", embed=embed)

        await self._google_api.cancel_scrim(scrim)

    @_handle_automatic_error
    async def _scrim_request_created_cancelled(self, scrim: Scrim):
        if scrim in self._scrim_messages:
            await self._scrim_messages[scrim].delete()
            self._scrim_messages.pop(scrim)

        embed = DiscordStuff.create_scrim_request_created_cancelled_embed(scrim)
        await self._scrim_channel.send(f"<@&{MANAGER_ROLE_ID}>", embed=embed)

    @_handle_automatic_error
    async def _scrim_request_resent(self, scrim: Scrim):
        if scrim in self._scrim_messages:
            await self._scrim_messages[scrim].delete()

        embed =DiscordStuff.create_scrim_request_resent_embed(scrim)
        self._scrim_messages[scrim] = await self._scrim_channel.send(f"<@&{MANAGER_ROLE_ID}>", embed=embed)

    @_handle_automatic_error
    async def _scrim_request_updated(self, new_scrim: Scrim, old_scrim: Scrim):
        if old_scrim in self._scrim_messages:
            await self._scrim_messages[old_scrim].delete()
            self._scrim_messages.pop(old_scrim)

        embed =DiscordStuff.create_scrim_request_updated_embed(new_scrim)
        self._scrim_messages[new_scrim] = await self._scrim_channel.send(f"<@&{MANAGER_ROLE_ID}>", embed=embed)

    @_handle_automatic_error
    async def _scrim_request_updated_booked(self, new_scrim: Scrim, old_scrim: Scrim):
        if old_scrim in self._scrim_messages:
            self._scrim_messages[new_scrim] = self._scrim_messages.pop(old_scrim)

        await self._scrim_request_booked(new_scrim)

    @_handle_automatic_error
    async def _scrim_request_wildcard_updated_booked(self, new_scrim: Scrim, old_scrim: Scrim):
        if old_scrim in self._scrim_messages:
            self._scrim_messages[new_scrim] = self._scrim_messages.pop(old_scrim)

        await self._scrim_request_wildcard_booked(new_scrim)

    @_handle_automatic_error
    async def _scrim_request_booked_updated(self, new_scrim: Scrim, old_scrim: Scrim):
        if old_scrim in self._scrim_messages:
            await self._scrim_messages[old_scrim].delete()
            self._scrim_messages.pop(old_scrim)

        embed =DiscordStuff.create_scrim_request_booked_updated_embed(new_scrim)
        self._scrim_messages[new_scrim] = await self._scrim_channel.send(f"<@&{CRYOBARK_ROLE_ID}>", embed=embed)

        await self._google_api.cancel_scrim(old_scrim)
        await self._google_api.found_scrim(new_scrim)

    @_handle_automatic_error
    async def _scrim_request_wildcard_booked(self, scrim: Scrim):
        # Found wildcard
        if scrim in self._scrim_messages:
            await self._scrim_messages[scrim].delete()

        embed =DiscordStuff.create_scrim_request_wildcard_booked_embed(scrim)
        self._scrim_messages[scrim] = await self._scrim_channel.send(f"<@&{CRYOBARK_ROLE_ID}>", embed=embed)

    @_handle_automatic_error
    async def _scrim_request_wildcard_booked_updated(self, new_scrim: Scrim, old_scrim: Scrim):
        # Changed format of one wildcard scrim to another format
        if old_scrim in self._scrim_messages:
            await self._scrim_messages[old_scrim].delete()
            self._scrim_messages.pop(old_scrim)

        embed =DiscordStuff.create_scrim_request_wildcard_booked_updated_embed(new_scrim)
        self._scrim_messages[new_scrim] = await self._scrim_channel.send(f"<@&{CRYOBARK_ROLE_ID}>", embed=embed)

    @_handle_automatic_error
    async def _scrim_played(self, scrim: Scrim):
        if scrim in self._scrim_messages:
            await self._scrim_messages[scrim].delete()
            self._scrim_messages.pop(scrim)

        embed =DiscordStuff.create_scrim_played_embed(scrim)
        await self._scrim_channel.send(embed=embed)

        await self._google_api.update_scrim_results()

    @_handle_automatic_error
    async def _scrim_request_passed(self, scrim: Scrim):
        if scrim in self._scrim_messages:
            await self._scrim_messages[scrim].delete()
            self._scrim_messages.pop(scrim)

    @_handle_automatic_error
    async def _incoming_scrim_request_removed(self, scrim: Scrim):
        for scrim_request_message in self._incoming_scrim_request_messages:
            if scrim_request_message[0].equals_exact(scrim):
                await scrim_request_message[1].delete()
                self._incoming_scrim_request_messages.remove(scrim_request_message)
                break

    @_handle_automatic_error
    async def _incoming_scrim_request_recieved(self, scrim: Scrim):
        embed = DiscordStuff.create_scrim_request_recieved_embed(scrim)
        self._incoming_scrim_request_messages.append((scrim, await self._scrim_channel.send(f"<@&{MANAGER_ROLE_ID}>", embed=embed)))

    @_handle_automatic_error
    async def _outgoing_scrim_request_removed(self, scrim: Scrim):
        for scrim_request_message in self._outgoing_scrim_request_messages:
            if scrim_request_message[0].equals_exact(scrim):
                await scrim_request_message[1].delete()
                self._outgoing_scrim_request_messages.remove(scrim_request_message)
                break

    @_handle_automatic_error
    async def _outgoing_scrim_request_recieved(self, scrim: Scrim):
        embed = DiscordStuff.create_scrim_request_sent_embed(scrim)
        self._outgoing_scrim_request_messages.append((scrim, await self._scrim_channel.send(f"<@&{MANAGER_ROLE_ID}>", embed=embed)))


if __name__ == "__main__":
    bot = CryoBot()