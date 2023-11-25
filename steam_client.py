from steam import Steam
from decouple import config
from datetime import datetime

steam = Steam("token")



def steamgetuser(user, identifier):

  print("Fetching Account...")
  
  if identifier == 0:
     userdetails = dict(steam.users.search_user(user))
  if identifier == 1:
     userdetails = dict(steam.users.get_user_details(user))


  print(userdetails["player"])
  steamid = userdetails["player"]["steamid"]
  avatarfull = userdetails["player"]["avatarfull"]
  persona_name = userdetails["player"]["personaname"]
  communityvisiblity = userdetails["player"]["communityvisibilitystate"]
  
  if communityvisiblity == 3:
   creation_timestamp = userdetails["player"]["timecreated"]
   creation_date = datetime.fromtimestamp(creation_timestamp)
   persona_state = userdetails["player"]["personastate"]
   online_status = ""
   badges = steam.users.get_user_badges(steamid)

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
   level = str(level).replace("{'player_level': ", "").replace("}", "")
   steamAccountInfo = [steamid, avatarfull, persona_name, online_status, level, creation_date, badges]
   print("Retrieved Account.")
   return steamAccountInfo


  else: 
    steamAccountInfo = [steamid, avatarfull, persona_name]
    print("Retrieved Account.")
    return steamAccountInfo
  
  



def steamgetownedgames(id, ctx):
  print("Fetching owned games...")

  gamesDict = steam.users.get_owned_games(id)
  
  if len(gamesDict) != 0:
   numberofOwnedGames = gamesDict["game_count"]
   games = gamesDict["games"]
   ownedGamesInformation = [numberofOwnedGames, games]
   print("Retrieved Games.")

   return ownedGamesInformation
  
  else:
    ownedGamesInformation = None
    return ownedGamesInformation
    


def steamgetfriends(id):

   print("Fetching friends list...")
   friendslist = dict(steam.users.get_user_friends_list(id))  
   print("Retrieved Friends List.")
   return friendslist
  


def steamgetgamepage(game, ctx):
  requestedGameFound = False
  gameSearch = dict(steam.apps.search_games(game))

  for x in range(len(gameSearch["apps"])):
    apiGame = gameSearch["apps"][x]["name"].lower().replace("\\u2122", "").replace("\\u00ae","").replace("\\u2019", "'")
  
    if apiGame == game.lower():
      requestedGameFound = True
      gameID = gameSearch["apps"][x]["id"]
      gamePrice = gameSearch["apps"][x]["price"]

      if gamePrice == "" :
        gamePrice = "Unspecified"
        return
      break
    else: 
      requestedGameFound = False
  
    
  if requestedGameFound == True:
     gamePage = steam.apps.get_app_details(gameID)
     gameName = gamePage[str(gameID)]["data"]["name"]
     
     try:
      gameAchievements = gamePage[str(gameID)]["data"]["achievements"]
     except:
       gameAchievements = None

     gameDescription = gamePage[str(gameID)]["data"]["short_description"]
     gameImage = gamePage[str(gameID)]["data"]["header_image"]
     gameDevs = gamePage[str(gameID)]["data"]["developers"]
     gamePublishers = gamePage[str(gameID)]["data"]["publishers"]
     try:
      recommendations = gamePage[str(gameID)]["data"]["recommendations"]["total"]
     except:
       recommendations = "N/A"
     gameInformation = [gameName, gameDescription, gameImage, gameSearch, gamePrice, gameAchievements, gameDevs, gamePublishers, recommendations]
     

     return gameInformation
  
  if requestedGameFound == False:
     availableGames = []
     for x in range(len(gameSearch["apps"])):

      apiGame = gameSearch["apps"][x]["name"].replace("\\u2122", "").replace("\\u00ae","").replace("\\u2019", "'")
      availableGames.append(apiGame)

     if len(availableGames) != 0:
       return availableGames


