import random
from datetime import timedelta

import discord

from helper import getVariable, ordinal
from scrim_classes import Player, Scrim, Team

DISCORD_TOKEN: str = getVariable("DISCORD_TOKEN")
CHANNEL_ID: int = getVariable("CHANNEL_ID")
ZINSKI_ODDS: float = getVariable("ZINSKI_ODDS")

class DiscordStuff:
    """Handles all static methods to create discord things (Embeds, Polls, etc) that get returned and sent"""
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
            if random.random()  < ZINSKI_ODDS:
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
    def create_scrim_request_recieved_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim request is recieved

        Args:
            scrim (Scrim): The scrim request that was recieved

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
            rep = scrim.team.reputation.gank_rep
        embed.add_field(name="Team", value=scrim.team.name, inline=True)
        embed.add_field(name="Rank", value=scrim.team.rank.rank, inline=True)
        embed.add_field(name="GankRep", value=rep, inline=True)

        embed.set_author(name="OP.GG", url=scrim.team.opggLink, icon_url="https://play-lh.googleusercontent.com/FeRWKSHpYNEW21xZCQ-Y4AkKAaKVqLIy__PxmiE_kGN1uRh7eiB87ZFlp3j1DRp9r8k")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Assist_Me_ping.png")

        return embed

    @_embed
    def create_scrim_request_sent_embed(scrim: Scrim) -> discord.Embed:
        """
        Creates the embed to post when a scrim request is sent

        Args:
            scrim (Scrim): The scrim request that was sent out

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        embed = discord.Embed(
            title=f"Scrim Request Sent To {scrim.team.name}",
            description="Let's hope they accept! We're desperate!",
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
            rep = scrim.team.reputation.gank_rep
        embed.add_field(name="Team", value=scrim.team.name, inline=True)
        embed.add_field(name="Rank", value=scrim.team.rank.rank, inline=True)
        embed.add_field(name="GankRep", value=rep, inline=True)

        embed.set_author(name="OP.GG", url=scrim.team.opggLink, icon_url="https://play-lh.googleusercontent.com/FeRWKSHpYNEW21xZCQ-Y4AkKAaKVqLIy__PxmiE_kGN1uRh7eiB87ZFlp3j1DRp9r8k")

        embed.set_thumbnail(url="https://wiki.leagueoflegends.com/en-us/images/Hold_ping.png")

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

        rep = scrim.team.reputation.gank_rep if scrim.team.reputation else ""
        if scrim.team.name:
            embed.add_field(name="Team", value=scrim.team.name, inline=True)
        if scrim.team.rank:
            embed.add_field(name="Rank", value=scrim.team.rank.rank, inline=True)
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

        rep = scrim.team.reputation.gank_rep if scrim.team.reputation else ""
        if scrim.team.name:
            embed.add_field(name="Team", value=scrim.team.name, inline=True)
        if scrim.team.rank:
            embed.add_field(name="Rank", value=scrim.team.rank.rank, inline=True)
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

        rep = scrim.team.reputation.gank_rep if scrim.team.reputation else ""
        if scrim.team.name:
            embed.add_field(name="Team", value=scrim.team.name, inline=True)
        if scrim.team.rank:
            embed.add_field(name="Rank", value=scrim.team.rank.rank, inline=True)
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

    @_embed
    def create_team_data_embed(team: Team) -> discord.Embed:
        """
        Creates the embed to post to show team data

        Args:
            scrim (Scrim): The scrim that was updated

        Returns:
            embed (Embed): The discord embed that should be posted
        """
        description = team.bio
        mains: list[Player] = []
        subs: list[Player] = []
        for player in team.roster:
            if player.is_sub:
                subs.append(player)
            else:
                mains.append(player)

        if len(mains):
            description += "\n\nMain Roster:"
            for player in mains:
                description += f"\n[{player.name} | {player.rank}](https://op.gg/lol/summoners/{player.server}/{player.name.replace(' ', '%20')}-{player.tag})"

        if len(subs):
            description += "\n\nSubs:"
            for player in subs:
                description += f"\n[{player.name} | {player.rank}](https://op.gg/lol/summoners/{player.server}/{player.name.replace(' ', '%20')}-{player.tag})"

        embed = discord.Embed(
            title=team.name,
            description=description,
            color=discord.Color.purple(),
            url=f"https://lol.gankster.gg/teams/{team.number}"
        )

        embed.add_field(name="GankRep", value=team.reputation.gank_rep, inline=True)
        embed.add_field(name="Response\nRate", value=f"{int(team.reputation.response_rate * 100)}%", inline=True)
        embed.add_field(name="Cancellation\nRate", value=f"{int(team.reputation.cancellation_rate * 100)}%", inline=True)

        embed.add_field(name="Communication", value=team.reputation.communication, inline=True)
        embed.add_field(name="Behavior", value=team.reputation.behavior, inline=True)
        embed.add_field(name="On Time", value=team.reputation.on_time, inline=True)

        embed.add_field(name="Likes", value=team.reputation.likes, inline=True)
        embed.add_field(name="Dislikes", value=team.reputation.dislikes, inline=True)
        embed.add_field(name="Responds\nWithin", value=team.reputation.response_time.formatted_time(), inline=True)

        embed.set_thumbnail(url=team.logo_url if team.logo_url else "https://scontent-ord5-1.xx.fbcdn.net/v/t39.30808-6/361564138_269973222308481_6526154362229793324_n.jpg?_nc_cat=108&ccb=1-7&_nc_sid=6ee11a&_nc_ohc=uUl8jMkjKl0Q7kNvwGVRzj1&_nc_oc=Adk5vvRrbX_bkibGR9NqajI07fQJb2yMjK_a3KshkPXbaDD9O0ONrmiE55m7FzzuB4noHSa9R5uTuoeg4RZvB4Ma&_nc_zt=23&_nc_ht=scontent-ord5-1.xx&_nc_gid=Vrmy11sTxmffJL83Eu3thw&oh=00_AfZuVwgo988MXLf2Bvz-hBGkE_dy-xOn-o9MH473XwhYtw&oe=68D3E817")

        return embed