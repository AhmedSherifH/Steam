from steam import Steam
from decouple import config
from datetime import datetime

steam = Steam("TOKEN")
errorMessage = "User not found."

def steamgetuser(user, identifier):
  print("Fetching Account...")
  
  if identifier == 0:
    userdetails = dict(steam.users.search_user(user))
  if identifier == 1:
    userdetails = dict(steam.users.get_user_details(user))
  

  steamid = userdetails["player"]["steamid"]
  avatarfull = userdetails["player"]["avatarfull"]
  creation_timestamp = userdetails["player"]["timecreated"]
  persona_state = userdetails["player"]["personastate"]
  persona_name = userdetails["player"]["personaname"]
  online_status = ""
  badges = steam.users.get_user_badges(steamid)
  creation_date = datetime.fromtimestamp(creation_timestamp)

  match persona_state:
    case 0:
      online_status = "Offline"
    case 1:
      online_status = "Online"
    case 2:
      online_status = "Busy"
    case 3:
      online_status = "Away"
    case 4:
      online_status = "Snooze"
    case 5:
      online_status = "Looking to Trade"
    case 6:
      online_status = "Looking to Play"

  level = steam.users.get_user_steam_level(steamid)
  #{'player_level': 16}
  level = str(level).replace("{'player_level': ", "").replace("}", "")
  #16   
  steamAccountInfo = [steamid, avatarfull, creation_date, online_status, level, persona_name, badges]
  print("Retrieved Account.")
  return steamAccountInfo


def steamgetownedgames(id):
  print("Fetching owned games...")
  gamesDict = steam.users.get_owned_games(id)
  numberofOwnedGames = gamesDict["game_count"]
  games = gamesDict["games"]

  ownedGamesInformation = [numberofOwnedGames, games]
  print("Retrieved Games.")
  return ownedGamesInformation

def steamgetfriends(id):
  print("Fetching friends list...")
  friendslist = dict(steam.users.get_user_friends_list(id))
  print("Retrieved Friends List.")
  return friendslist

async def steamgetgamepage(game, ctx):
  gameSearch = dict(steam.apps.search_games(game))
  print(gameSearch)
  for x in range(len(gameSearch["apps"])):
    print(gameSearch["apps"][x])
    print(game)
    apiGame = gameSearch["apps"][x]["name"].lower().replace("\\u2122", "").replace("\\u00ae","").replace("\\u2019", "'")
    if apiGame == game.lower():
      gameID = gameSearch["apps"][x]["id"]
      try:
       gamePrice = gameSearch["apps"][x]["price"]
       if gamePrice == "" :
        gamePrice = "Unspecified"
        return
      except: 
        gamePrice = "Unspecified"
        return
     

       


  

  try:
   gamePage = steam.apps.get_app_details(gameID)
   gameName = gamePage[str(gameID)]["data"]["name"]
   gameAchievements = gamePage[str(gameID)]["data"]["achievements"]
   gameDescription = gamePage[str(gameID)]["data"]["short_description"]
   gameImage = gamePage[str(gameID)]["data"]["header_image"]
   gameInformation = [gameName, gameDescription, gameImage, gameSearch, gamePrice, gameAchievements]
   return gameInformation
  except:
   availableGames = []
   for x in range(len(gameSearch["apps"])):
    apiGame = gameSearch["apps"][x]["name"].replace("\\u2122", "").replace("\\u00ae","").replace("\\u2019", "'")
    availableGames.append(apiGame)
   if len(availableGames) != 0:
    return availableGames


