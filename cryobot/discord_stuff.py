import discord
from scrim_classes import Scrim
from helper import getVariable
from random import random

DISCORD_TOKEN = getVariable("DISCORD_TOKEN")
CHANNEL_ID = getVariable("CHANNEL_ID")
ZINSKI_ODDS = getVariable("ZINSKI_ODDS")

class DiscordStuff:
    def create_weekly_poll(start, end):
        """
        Creates the URL, headers, and payload for the weekly availibility poll

        Args:
            start (str): The starting date for the duration (Monday)
            accept (str): The starting date for the duration (Sunday)

        Returns:
            url (str): the session url to post
            headers (dict): the headers to post
            payload (dict): the payload to post
        """
        url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"

        headers = {
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "Content-Type": "application/json"
        }

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
        return url, headers, payload

    def _embed(func):
        """Decorator to add a standard footer to discord embeds"""
        def wrapper(*args, **kwargs):
            embed: discord.Embed = func(*args, **kwargs)
            if random()  < ZINSKI_ODDS:
                embed.set_footer(text="Hi Zinski :D")
            return embed
        return wrapper

    @_embed
    def create_looking_for_scrim_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim is being sought out

        Args:
            scrim (Scrim): The scrim that is being sought out

        Returns:
            embed (Embed): the discord embed that should be posted
        """
        embed = discord.Embed(
            title="Scrim Request Sent",
            description="Cryobark has sent out a request for a scrim!",
            color=discord.Color.gold()
        )

        dateString = scrim.time.strftime("%A, %B %d")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrimFormat.format_short, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Enemy_Missing_ping.png")

        return embed

    @_embed
    def create_scrcim_request_recieved_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim request is recieved

        Args:
            scrim (Scrim): The scrim request that was sent out

        Returns:
            embed (Embed): the discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Request Recieved From {scrim.team.name}",
            description="Should you accept or decline? The choice is yours!",
            color=discord.Color.green(),
            url=f"https://lol.gankster.gg/teams/{scrim.team.number}"
        )

        dateString = scrim.time.strftime("%A, %B %d")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrimFormat.format_short, inline=True)

        rep = ""
        if scrim.team.reputation:
            rep = scrim.team.reputation.gankRep
        embed.add_field(name="Team", value=scrim.team.name, inline=True)
        embed.add_field(name="Rank", value=scrim.team.rank, inline=True)
        embed.add_field(name="GankRep", value=rep, inline=True)

        embed.set_author(name="OP.GG", url=scrim.team.opggLink, icon_url="https://play-lh.googleusercontent.com/FeRWKSHpYNEW21xZCQ-Y4AkKAaKVqLIy__PxmiE_kGN1uRh7eiB87ZFlp3j1DRp9r8k")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Assist_Me_ping.png")

        return embed

    @_embed
    def create_scrim_found_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim is confirmed

        Args:
            scrim (Scrim): The scrim that was found and confirmed

        Returns:
            embed (Embed): the discord embed that should be posted
        """
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
        embed.add_field(name="Format", value=scrim.scrimFormat.format_short, inline=True)

        rep = ""
        if scrim.team.reputation:
            rep = scrim.team.reputation.gankRep
        embed.add_field(name="Team", value=scrim.team.name, inline=True)
        embed.add_field(name="Rank", value=scrim.team.rank, inline=True)
        embed.add_field(name="GankRep", value=rep, inline=True)

        embed.set_author(name="OP.GG", url=scrim.team.opggLink, icon_url="https://play-lh.googleusercontent.com/FeRWKSHpYNEW21xZCQ-Y4AkKAaKVqLIy__PxmiE_kGN1uRh7eiB87ZFlp3j1DRp9r8k")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/On_My_Way_ping.png") #I updated this on the wiki so I could use the correct looking one :D

        return embed

    @_embed
    def create_scrim_cancelled_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim is cancelled

        Args:
            scrim (Scrim): The scrim that was cancelled

        Returns:
            embed (Embed): the discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Cancelled vs {scrim.team.name}",
            description=f"Darn {scrim.team.name} how unreliable!",
            color=discord.Color.red()
        )

        dateString = scrim.time.strftime("%A, %B %d")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrimFormat.format_short, inline=True)

        # rep = ""
        # if scrim.team.reputation:
        #     rep = scrim.team.reputation.gankRep
        # embed.add_field(name="Team", value=scrim.team.name, inline=True)
        # embed.add_field(name="Rank", value=scrim.team.rank, inline=True)
        # embed.add_field(name="GankRep", value=rep, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Retreat_ping.png")

        return embed