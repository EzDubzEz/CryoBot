import discord
from scrim_classes import Scrim
from helper import getVariable, ordinal
from random import random
from datetime import timedelta

DISCORD_TOKEN: str = getVariable("DISCORD_TOKEN")
CHANNEL_ID: int = getVariable("CHANNEL_ID")
ZINSKI_ODDS: float = getVariable("ZINSKI_ODDS")

class DiscordStuff:
    def create_weekly_poll(start, end) -> discord.Poll:
        """
        Creates the Poll for the weekly availibility poll

        Args:
            start (str): The starting date for the duration (Monday)
            accept (str): The starting date for the duration (Sunday)

        Returns:
            poll (Poll): The poll that should be posted
        """
        poll = discord.Poll(question=f"Scrim Availability {start} - {end}", duration=timedelta(hours=40))
        poll.add_answer(text="Monday")
        poll.add_answer(text="Tuesday")
        poll.add_answer(text="Wednesday")
        poll.add_answer(text="Thursday")
        poll.add_answer(text="Friday")
        poll.add_answer(text="Midday Saturday")
        poll.add_answer(text="Night Saturday")
        poll.add_answer(text="Midday Sunday")
        poll.add_answer(text="Night Sunday")
        poll.multiple = True

        return poll

    def _embed(func):
        """ Decorator to add a footer to discord embeds """
        def wrapper(*args, **kwargs):
            embed: discord.Embed = func(*args, **kwargs)
            if random()  < ZINSKI_ODDS:
                embed.set_footer(text="Hi Zinski :D")
            return embed
        return wrapper

    @_embed
    def create_scrim_request_created_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim is being sought out

        Args:
            scrim (Scrim): The scrim that is being sought out

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title="Scrim Request Sent",
            description="Cryobark has sent out a request for a scrim!",
            color=discord.Color.gold()
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Enemy_Missing_ping.png")

        return embed

    @_embed
    def create_scrcim_request_recieved_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim request is recieved

        Args:
            scrim (Scrim): The scrim request that was sent out

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Request Recieved From {scrim.team.name}",
            description="Should you accept or decline? The choice is yours!",
            color=discord.Color.green(),
            url=f"https://lol.gankster.gg/teams/{scrim.team.number}"
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

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
    def create_scrim_request_booked_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim is confirmed

        Args:
            scrim (Scrim): The scrim that was found and confirmed

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Found vs {scrim.team.name}",
            description="Get ready to rumble!",
            color=discord.Color.blue(),
            url=f"https://lol.gankster.gg/teams/{scrim.team.number}"
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

        rep = scrim.team.reputation.gankRep if scrim.team.reputation else ""
        if scrim.team.name:
            embed.add_field(name="Team", value=scrim.team.name, inline=True)
        if scrim.team.rank:
            embed.add_field(name="Rank", value=scrim.team.rank, inline=True)
        if rep:
            embed.add_field(name="GankRep", value=rep, inline=True)

        if scrim.team.opggLink:
            embed.set_author(name="OP.GG", url=scrim.team.opggLink, icon_url="https://play-lh.googleusercontent.com/FeRWKSHpYNEW21xZCQ-Y4AkKAaKVqLIy__PxmiE_kGN1uRh7eiB87ZFlp3j1DRp9r8k")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/On_My_Way_ping.png") #I updated this on the wiki so I could use the correct looking one :D

        return embed

    @_embed
    def create_scrim_played_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim is confirmed

        Args:
            scrim (Scrim): The scrim that was found and confirmed

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Played vs {scrim.team.name}",
            description="You guys gave it your all! gg!",
            color=discord.Color.blue(),
            url=f"https://lol.gankster.gg/teams/{scrim.team.number}"
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

        rep = scrim.team.reputation.gankRep if scrim.team.reputation else ""
        if scrim.team.name:
            embed.add_field(name="Team", value=scrim.team.name, inline=True)
        if scrim.team.rank:
            embed.add_field(name="Rank", value=scrim.team.rank, inline=True)
        if rep:
            embed.add_field(name="GankRep", value=rep, inline=True)

        if scrim.team.opggLink:
            embed.set_author(name="OP.GG", url=scrim.team.opggLink, icon_url="https://play-lh.googleusercontent.com/FeRWKSHpYNEW21xZCQ-Y4AkKAaKVqLIy__PxmiE_kGN1uRh7eiB87ZFlp3j1DRp9r8k")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Vision_Cleared_ping.png")

        return embed

    @_embed
    def create_scrim_request_found_cancelled_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim is cancelled

        Args:
            scrim (Scrim): The scrim that was cancelled

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Cancelled vs {scrim.team.name}",
            description=f"Darn {scrim.team.name} how unreliable!",
            color=discord.Color.red()
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Retreat_ping.png")

        return embed

    @_embed
    def create_scrim_request_created_cancelled_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim request is cancelled

        Args:
            scrim (Scrim): The scrim that was cancelled

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Request Withdrawn",
            description=f"Darn Cryobark how unreliable!\nMaybe we can play some flex?",
            color=discord.Color.red()
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Retreat_ping.png")

        return embed

    @_embed
    def create_scrim_request_resent_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim request is resent after a cancellation

        Args:
            scrim (Scrim): The scrim that was cancelled/resent

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Request Resent",
            description=f"We're back on the hunt! Lets get another scrim!",
            color=discord.Color.gold()
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Enemy_Missing_ping.png")

        return embed

    @_embed
    def create_scrim_request_updated_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim request is updated

        Args:
            scrim (Scrim): The scrim that was updated

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Request Updated",
            description=f"Check out these new and improved details!",
            color=discord.Color.gold()
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Enemy_Missing_ping.png")

        return embed

    @_embed
    def create_scrim_request_booked_updated_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a confirmed scrim request is updated

        Args:
            scrim (Scrim): The scrim that was updated

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Updated vs {scrim.team.name}",
            description="Check out these new and improved details and get ready to rumble!",
            color=discord.Color.blue(),
            url=f"https://lol.gankster.gg/teams/{scrim.team.number}"
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

        rep = scrim.team.reputation.gankRep if scrim.team.reputation else ""
        if scrim.team.name:
            embed.add_field(name="Team", value=scrim.team.name, inline=True)
        if scrim.team.rank:
            embed.add_field(name="Rank", value=scrim.team.rank, inline=True)
        if rep:
            embed.add_field(name="GankRep", value=rep, inline=True)

        if scrim.team.opggLink:
            embed.set_author(name="OP.GG", url=scrim.team.opggLink, icon_url="https://play-lh.googleusercontent.com/FeRWKSHpYNEW21xZCQ-Y4AkKAaKVqLIy__PxmiE_kGN1uRh7eiB87ZFlp3j1DRp9r8k")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/On_My_Way_ping.png") #I updated this on the wiki so I could use the correct looking one :D

        return embed

    @_embed
    def create_scrim_request_wildcard_booked_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim is confirmed but team is unknown

        Args:
            scrim (Scrim): The scrim that was found and confirmed

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Found",
            description="Get ready to rumble! Couldn't determine the enemy team.",
            color=discord.Color.blue(),
            url=f"https://lol.gankster.gg/teams/{scrim.team.number}"
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/On_My_Way_ping.png") #I updated this on the wiki so I could use the correct looking one :D

        return embed

    @_embed
    def create_scrim_request_wildcard_booked_updated_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a confirmed scrim request with unkown team is updated 

        Args:
            scrim (Scrim): The scrim that was updated

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Updated",
            description="Check out these new and improved details and get ready to rumble!! Couldn't determine the enemy team.",
            color=discord.Color.blue(),
            url=f"https://lol.gankster.gg/teams/{scrim.team.number}"
        )

        dateString = scrim.time.strftime(f"%A, %b {ordinal(scrim.time.day)}")
        timeString = scrim.time.strftime("%I:%M %p").lstrip("0")
        embed.add_field(name="Date", value=dateString, inline=True)
        embed.add_field(name="Time", value=timeString, inline=True)
        embed.add_field(name="Format", value=scrim.scrim_format.format_short, inline=True)

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/On_My_Way_ping.png") #I updated this on the wiki so I could use the correct looking one :D

        return embed
