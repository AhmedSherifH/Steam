from typing import Optional
from datetime import datetime
import discord
from discord.ext import commands
from discord.ui import *
from steam_client import *
import discord.utils
import math
import sqlite3

db = sqlite3.connect("profiles.db")
cursor = db.cursor()



intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

@bot.event
async def on_ready():
    print("Logged on as ", bot.user)

@bot.command()
async def help(ctx):
   embed = discord.Embed(title=f"Steam Information Help")
   embed.set_thumbnail(url="https://img.icons8.com/ios-filled/100/steam-circled.png")
   embed.add_field(name="My prefix is `!`",
                  value="**__Commands__** \n > :adult: `!user <steam-username>`: Returns steam account information. \n > :id: `!userid <steam-id>`: Returns steam account information. \n > :video_game: `!game <game-name>`: Returns game information including the price, description and developers. \n > :link: `!link <steam-id>`: Add your profile to the bot's database where you'll be able to retrieve your account's information by using `!profile` \n > :x: `!unlink`: Remove the steam account that's linked.")
   embed.add_field(name="**__Tips__**", value="> :arrow_right: Press the `Owned Games` and `Friends List` buttons multiple times to navigate through pages. \n > :arrow_right: The `!game` command has a search function; it returns a list of games that have similar names. The search is usually executed automatically when there is a misspelling or missing keywords.", inline=False)
   embed.description = "This bot is open source. Feel free to contribute on [Github](https://github.com/AhmedSherifH/Steam/)"
   await ctx.send(embed=embed)
   


@bot.command()
async def user(ctx, args):
    user = str(args)
    steamAccount = steamgetuser(user, identifier=0)
    profileMenu = profilemenuView(steamAccount, ctx)
    embed = summaryEmbed(steamAccount)
    await ctx.send(embed=embed, view=profileMenu)


@bot.command()
async def userid(ctx, args):
 try:
    user = str(args)
    steamAccount = steamgetuser(user, identifier=1)
    profileMenu = profilemenuView(steamAccount, ctx)
    embed = summaryEmbed(steamAccount)
    await ctx.send(embed=embed, view = profileMenu)
 except:
    await ctx.send("Could not find user.")


@bot.command()
async def game(ctx, *, args):
    try:
        game = str(args)
        gameInformation = steamgetgamepage(game, ctx)
        gamePageMenu = gamemenuView(gameInformation, ctx)
        embed = gameInformationEmbed(gameInformation)
        await ctx.send(embed=embed, view=gamePageMenu) 
    except:
        game = str(args)
        availableGames = steamgetgamepage(game, ctx)
        if availableGames != None:
         embed = availableGamesEmbed(availableGames)
         await ctx.send(embed=embed)
        else:
         await ctx.send("No game found.")

@bot.command()
async def link(ctx, *, args):
   steamID = str(args)
   discordID = ctx.author.id
   steamInformation = steamgetuser(steamID, identifier=1)
   linkingmenuViewEmbed = linkingmenuView(discordID, steamID)
   embed = linkingEmbed(steamInformation)
   await ctx.send(embed=embed, view=linkingmenuViewEmbed)

@bot.command()
async def profile(ctx):
  try: 
   discordID = ctx.author.id
   cursor.execute(f"SELECT steam_id FROM profiles WHERE discord_id = {discordID}")
   row = cursor.fetchall()
   #[('76561198434096480',)]
   id = str(row).replace("[", "").replace('"', "").replace("(", "").replace("'", "")   
   id = id.replace(",", "").replace(")", "").replace("]", "")
   steamAccount = steamgetuser(id, identifier=1)
   profileMenu = profilemenuView(steamAccount, ctx)
   embed = summaryEmbed(steamAccount)
   await ctx.send(embed=embed, view = profileMenu)
  except Exception as e:
     if str(e) == "list index out of range":
      embed = discord.Embed(title="User does not have a connected account.")
      await ctx.send(embed=embed)   
@bot.command()
async def unlink(ctx):
    discordID = ctx.author.id
    cursor.execute(f"DELETE FROM profiles WHERE discord_id = {discordID}")
    db.commit()
    embed = discord.Embed(title="Successfully unlinked")
    await ctx.send(embed=embed)
 
   

class linkingmenuView(discord.ui.View):
   def __init__(self, discordID, steamID):
      self.discordID = discordID
      self.steamID = steamID
      super().__init__()
   
   @discord.ui.button(label="Link", emoji="🔗")
   async def link_account(self, interaction: discord.Interaction, button: discord.ui.Button):
     try:
      cursor.execute(f"INSERT INTO profiles VALUES('{self.discordID}', '{self.steamID}')")
      db.commit()
      embed = discord.Embed(title="Linking successful")
      await interaction.response.edit_message(embed=embed, view=None)
     except Exception as e:
        if str(e) == "UNIQUE constraint failed: profiles.steam_id" or str(e) == "UNIQUE constraint failed: profiles.discord_id":
         embed = discord.Embed(title="Linking unsuccessful.")
         embed.add_field(name="", value="Make sure you don't already have an account linked.")
         await interaction.response.edit_message(embed=embed, view=None)
   @discord.ui.button(label="Ignore", emoji="❌")
   async def ignore_linking_request(self, interaction: discord.Interaction, button: discord.ui.Button):
      embed = discord.Embed(title="Linking request has been ignored")
      await interaction.response.edit_message(embed=embed, view=None)
      
      
    

class profilemenuView(discord.ui.View):
    def __init__(self, steamAccount, ctx):
        self.steamAccount = steamAccount
        self.ctx = ctx
        self.gameIndex = 0
        self.friendsIndex = 0
        super().__init__()

    @discord.ui.button(label="Owned Games", emoji="🎮")
    async def games_button(self, interaction: discord.Interaction, button: discord.ui.Button):
     # try:
        newGamesPage =  ownedGamesEmbed(self.steamAccount, self.ctx, self.gameIndex)
        self.gameIndex += 1
        if newGamesPage != None:
         await interaction.response.edit_message(embed=newGamesPage)

    @discord.ui.button(label="Profile Summary", emoji="🧭")
    async def profile_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        newProfilePage = summaryEmbed(self.steamAccount)
        await interaction.response.edit_message(embed=newProfilePage)

    @discord.ui.button(label="Friends List", emoji="🙎‍♂️")
    async def friends_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
         self.friendsIndex += 1
         newfriendsPage = friendsEmbed(self.steamAccount, self.ctx, self.friendsIndex)
         await interaction.response.edit_message(embed=newfriendsPage)
        except Exception as e:
          friendslistUnauthorizedEmbed = discord.Embed(title=f"{self.steamAccount[2]}'s Friends.")
          friendslistUnauthorizedEmbed.add_field(name="Could not get friends.", value="This can be caused if the user has hidden their friends list.")
          await interaction.response.edit_message(embed=friendslistUnauthorizedEmbed)

class gamemenuView(discord.ui.View):
    def __init__(self, gameInformation, ctx):
        self.gameInformation = gameInformation
        self.ctx = ctx
        super().__init__()

    @discord.ui.button(label="Achievements", emoji="🏆")
    async def achievements_Button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
         showachievementsEmbed = achievementsEmbed(self.gameInformation)
         await interaction.response.edit_message(embed=showachievementsEmbed)
        except:
            embed = discord.Embed(title="Highlighted Achievements")
            embed.add_field(name="", value="No achievements found.")
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Game Overview", emoji="🎮")
    async def game_overview_Button(self, interaction: discord.Interaction, button: discord.ui.Button):
        showGamePage = gameInformationEmbed(self.gameInformation)   
        await interaction.response.edit_message(embed=showGamePage)





 
def summaryEmbed(steamAccount):
  try:
    embed = discord.Embed(title=steamAccount[0])
    embed.set_thumbnail(url=steamAccount[1])
    embed.add_field(name="Date Created", 
                    value=steamAccount[5],
                    inline=True)
    
    embed.add_field(name="Online Status",
                    value=steamAccount[3],
                    inline=True)
    
    embed.add_field(name="Steam Level", 
                    value=f"{steamAccount[4]}",
                    inline=True)
    
    embed.add_field(name="Number of Badges", 
                    value=len(steamAccount[6]["badges"]), 
                    inline=False)
        
    embed.set_author(name=steamAccount[2])

    return embed
  
  except:
    embed = discord.Embed(title=steamAccount[0])
    embed.set_thumbnail(url=steamAccount[1])
    embed.set_author(name=steamAccount[2])
    embed.add_field(name="Cannot view profile.", value="The user has set their account to private")
    return embed

def ownedGamesEmbed(steamAccount, ctx, index):
    
    returnedOwnedGames =  steamgetownedgames(steamAccount[0], ctx)
    
    if returnedOwnedGames != None:
     
     embed = discord.Embed(title=f"{steamAccount[2]}'s Games")

     embed.set_thumbnail(url=steamAccount[1]) 

     embed.set_footer(text=f"Number of owned games: {returnedOwnedGames[0]}")
     
     indexedGames = returnedOwnedGames[1]
     
     index = index%int(math.ceil(len(indexedGames)/10))
     
     def page(index):
         return indexedGames[index * 10: index * 10 + 10]
     showGames = page(index)

     if len(showGames) != 0:
      for x in range(len(showGames)):  
             playtime = round(int(showGames[x]["playtime_forever"]) / 60)
             embed.add_field(
                name=showGames[x]["name"],
                value=f"{playtime} hours played.") 
     
     return embed
    
    else: 
        embed = discord.Embed(title=f"{steamAccount[2]}'s Games")
        embed.add_field(name="Could not get games.", value="This can be caused if the user has hidden their owned games.")
        return embed

      


def friendsEmbed(steamAccount, ctx, index):
    friendslist = steamgetfriends(steamAccount[0])
     
    indexedFriends = friendslist["friends"]
    index = index%int(math.ceil(len(indexedFriends)/10))

    def page(index):
         return indexedFriends[index * 10: index * 10 + 10]
    showFriends = page(index)

    embed = discord.Embed(title=f"{steamAccount[2]}'s Friends")
    embed.set_thumbnail(url=steamAccount[1])

    for x in range(int(len(showFriends))):
        friend_since = datetime.fromtimestamp(
            int(showFriends[x]["friend_since"])
        )

        embed.add_field(
            name=showFriends[x]["personaname"],
            value=f"Friends since: {friend_since}",
        )

    return embed


def gameInformationEmbed(gameInformation):
    embed = discord.Embed(title=f"{gameInformation[0]}")

    embed.add_field(name="Description", 
                    value=gameInformation[1],
                     inline=False)
    

    embed.add_field(name="Developers",
                    value=",\n".join(gameInformation[6]),
                    inline=True)
    
    embed.add_field(name="Price", 
                    value=gameInformation[4],
                    inline=True)

    embed.add_field(name="Publishers",
                    value=",\n".join(gameInformation[7]),
                    inline=False)
    
    embed.add_field(name="Recommendations",
                    value=gameInformation[8])
   
    embed.set_image(url=f"{gameInformation[2]}")

    return embed


def availableGamesEmbed(availableGames):
    embed = discord.Embed(title="Available Games")

    numbering = 1
    for game in availableGames:
         embed.add_field(name="", 
                         value=f"{numbering}: {game}", 
                         inline=False)
         numbering += 1
    return embed

def achievementsEmbed(gameInfromation):
   embed = discord.Embed(title="Highlighted Achievements")
   embed.set_footer(text=f"Total Number of Achievements: {gameInfromation[5]['total']}")

   numbering = 1

   for x in range(len(gameInfromation[5]["highlighted"])):
     achievement = gameInfromation[5]["highlighted"][x]["name"]

     embed.add_field(name="", 
                     value=f"{numbering}: {achievement}", 
                     inline=False)
     numbering += 1

   return embed

def linkingEmbed(steamInformation):
   embed = discord.Embed(title="Linking request")
   embed.add_field(name=f"{steamInformation[2]}", value=f"{steamInformation[0]}")
   embed.set_image(url=steamInformation[1])
   return embed

bot.run("TOKEN")

