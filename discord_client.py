from typing import Optional
from datetime import datetime
import discord
from discord.ext import commands
from discord.ui import *
from steam_client import *

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("Logged on as ", bot.user)


@bot.command()
async def user(ctx, args):
    user = str(args)
    steamAccount = steamgetuser(user, identifier=0)
    profileMenu = ProfileMenuView(steamAccount, ctx)
    embed = await summaryEmbed(steamAccount, ctx)
    await ctx.send(embed=embed, view=profileMenu)


# @bot.command()
# async def searchuserid(ctx, args):
#       user = str(args)
#       steamAccount = await steamgetuser(user, identifier=1)
#       profileMenu = ProfileMenuView(steamAccount, ctx)
#       embed = await summaryEmbed(steamAccount, ctx)
#       await ctx.send(embed=embed, view = profileMenu)


@bot.command()
async def game(ctx, *, args):
    try:
        game = str(args)
        gameInformation = steamgetgamepage(game, ctx)
        gamePageMenu = GameMenuView(gameInformation, ctx)
        embed = gameInformationEmbed(gameInformation)
        await ctx.send(embed=embed, view=gamePageMenu) 
    except:
        game = str(args)
        availableGames = steamgetgamepage(game, ctx)
        embed = availableGamesEmbed(availableGames)
        await ctx.send(embed=embed)


class ProfileMenuView(discord.ui.View):
    def __init__(self, steamAccount, ctx):
        self.steamAccount = steamAccount
        self.ctx = ctx
        super().__init__()

    @discord.ui.button(label="Owned Games", emoji="🎮")
    async def games_button(
        self, interaction: discord.Interaction, button: discord.ui.Button):
        newGamesPage = ownedGamesEmbed(self.steamAccount, self.ctx)
        await interaction.response.edit_message(embed=newGamesPage)

    @discord.ui.button(label="Profile Summary", emoji="🧭")
    async def profile_button(
        self, interaction: discord.Interaction, button: discord.ui.Button):
        newProfilePage = await summaryEmbed(self.steamAccount, self.ctx)
        await interaction.response.edit_message(embed=newProfilePage)

    @discord.ui.button(label="Friends List", emoji="🙎‍♂️")
    async def friends_button(
        self, interaction: discord.Interaction, button: discord.ui.Button):
        newfriendsPage = friendsEmbed(self.steamAccount, self.ctx)
        await interaction.response.edit_message(embed=newfriendsPage)

class GameMenuView(discord.ui.View):
    def __init__(self, gameInformation, ctx):
        self.gameInformation = gameInformation
        self.ctx = ctx
        super().__init__()
    @discord.ui.button(label="Achievements", emoji="🏆")
    async def achievements_Button(
        self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
         showachievementsEmbed = achievementsEmbed(self.gameInformation)
         await interaction.response.edit_message(embed=showachievementsEmbed)
        except:
            embed = discord.Embed(title="Highlighted Achievements")
            embed.add_field(name="", value="No achievements found.")
            await interaction.response.edit_message(embed=embed)
    @discord.ui.button(label="Game Overview", emoji="🎮")
    async def game_overview_Button(
        self, interaction: discord.Interaction, button: discord.ui.Button):
        showGamePage = gameInformationEmbed(self.gameInformation)   
        await interaction.response.edit_message(embed=showGamePage)



async def summaryEmbed(steamAccount, ctx):
    embed = discord.Embed(title=steamAccount[0])
    embed.set_thumbnail(url=steamAccount[1])
    embed.add_field(name="Date Created", value=steamAccount[2], inline=True)
    embed.add_field(name="Online Status", value=steamAccount[3], inline=True)
    embed.add_field(name="Steam Level", value=f"{steamAccount[4]}", inline=True)
    embed.add_field(
        name="Number of Badges", value=len(steamAccount[6]["badges"]), inline=False
    )
    embed.set_author(name=steamAccount[5])

    return embed


def ownedGamesEmbed(steamAccount, ctx):
    returnedOwnedGames = steamgetownedgames(steamAccount[0])
    embed = discord.Embed(title=f"{steamAccount[5]}'s Games")
    embed.set_thumbnail(url=steamAccount[1])
    embed.set_footer(text=f"Number of owned games: {returnedOwnedGames[0]}")

    for x in range(int(returnedOwnedGames[0])):
        playtime = round(int(returnedOwnedGames[1][x]["playtime_forever"]) / 60)
        embed.add_field(
            name=returnedOwnedGames[1][x]["name"], value=f"{playtime} hours played."
        )
    return embed


def friendsEmbed(steamAccount, ctx):
    friendslist = steamgetfriends(steamAccount[0])
    embed = discord.Embed(title=f"{steamAccount[5]}'s Friends")
    embed.set_thumbnail(url=steamAccount[1])
    for x in range(int(len(friendslist["friends"]))):
        friend_since = datetime.fromtimestamp(
            int(friendslist["friends"][x]["friend_since"])
        )
        embed.add_field(
            name=friendslist["friends"][x]["personaname"],
            value=f"Friends since: {friend_since}",
        )
    return embed


def gameInformationEmbed(gameInformation):
    embed = discord.Embed(title=f"{gameInformation[0]}")
    embed.add_field(name="Description", value=gameInformation[1], inline=True)
    embed.add_field(name="Price", value=gameInformation[4], inline=False)
    embed.set_image(url=f"{gameInformation[2]}")
    return embed


def availableGamesEmbed(availableGames):
    embed = discord.Embed(title="Available Games")
    numbering = 1
    for game in availableGames:
        embed.add_field(name="", value=f"{numbering}: {game}", inline=False)
        numbering += 1
    return embed

def achievementsEmbed(gameInfromation):
   embed = discord.Embed(title="Highlighted Achievements")
   embed.set_footer(text=f"Total Number of Achievements: {gameInfromation[5]['total']}")
   numbering = 1
   for x in range(len(gameInfromation[5]["highlighted"])):
     achievement = gameInfromation[5]["highlighted"][x]["name"]
     embed.add_field(name="", value=f"{numbering}: {achievement}", inline=True)
     numbering += 1
   return embed

bot.run("TOKEN")

