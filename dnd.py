import discord
import os
import json
from enum import Enum
import random
from dotenv import load_dotenv
from matches import Match
random.seed(111)
load_dotenv()
intents = discord.Intents(members = True, messages = True, message_content=True)
client = discord.Client(intents=intents)

class MatchState(Enum):
    TEAM_A_TURN = 1
    TEAM_B_TURN = 2


# def has_role(role_name, member):
default_path = "./examplefile.json"
flavor_text_path = "./flavor_text.json"
client_id = int(os.getenv("CLIENT_ID"))
channel_id = 877296962150498364

async def find_team_captain(team):
    captains = [i for i in teams[team] if teamData[i]["captain"]]
    return captains

async def write_params(param, default, channel):
    for key in teamData.keys():
        if param not in teamData[key]:
            teamData[key][param] = default
    await save(channel)

async def save(channel):
    if(gameStarted):
        await channel.send("Can't save right now")
    else:
        with open(default_path, 'w', encoding='utf-8') as file:
            json.dump(teamData, file)
        await channel.send("Saved successfully")


#TO-DO: Have the game be more interactive. Choose who the beater goes after
async def clean_up():
    global teamData
    for key, value in teamData.items():
        if(teamData[key]["injured"]):
            teamData[key]["injured"] = False
        if(teamData[key]["critically_injured"]):
            teamData[key]["critically_injured"] = False
            teamData[key]["injured"] = True


async def load_roster_from_file(file_name, roster_name):
    if roster_name not in temp_rosters:
        temp_rosters[roster_name] = {}
        temp_rosters[roster_name]["Beater1"] = ""
        temp_rosters[roster_name]["Beater2"] = ""
        temp_rosters[roster_name]["Chaser1"] = ""
        temp_rosters[roster_name]["Chaser2"] = ""
        temp_rosters[roster_name]["Chaser3"] = ""
        temp_rosters[roster_name]["Keeper"] = ""
        temp_rosters[roster_name]["Seeker"] = ""
    with open(file_name, "r", encoding="utf8") as file:
        for line in file:
            data = json.loads(line)
            print(data)
    for key, value in data.items():
        for position, player in value.items():
            if position not in temp_rosters[roster_name]:
                print("Invalid position name")
            else:
                if player not in teamData:
                    print("Invalid player name")
                else:
                    if(teamData[player]["team"] != key):
                        print("Player not in team")
                    else:
                        temp_rosters[roster_name][position] = player
        print(temp_rosters[roster_name])


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    global DEVELOPMENT_MODE
    global teamData
    global flavorText
    global gameType
    global gameStarted
    global currentMatch
    global control_sequence
    global teams
    global team_rosters
    global temp_rosters
    global teamA_score
    global teamB_score
    global team_list
    global help_string
    team_list = ["Gryffindor", "Gryffindor2", "Ravenclaw", "Ravenclaw2", "Slytherin", "Slytherin2", "Hufflepuff", "Hufflepuff2"]
    gameStarted = False
    DEVELOPMENT_MODE = True
    currentMatch = None
    teams = {}
    team_rosters = {}
    temp_rosters = {}
    teamA_score = 0
    teamB_score = 0
    with open(default_path, "r", encoding="utf8") as file:
        for line in file:
            teamData = json.loads(line)
    helper = []
    with open("help.txt", "r", encoding="utf8") as help:
        for line in help:
            helper.append(line)
    with open(flavor_text_path, "r", encoding="utf8") as f:
        for line in f:
            flavorText = json.loads(line)
    
    help_string = "".join(helper)
    for team in team_list:
        team_rosters[team] = {}
        teams[team] = []
        team_rosters[team]["Seeker"] = None
        team_rosters[team]["Chaser1"] = None
        team_rosters[team]["Chaser2"] = None
        team_rosters[team]["Chaser3"] = None
        team_rosters[team]["Beater1"] = None
        team_rosters[team]["Beater2"] = None
        team_rosters[team]["Keeper"] = None

    for key, value in teamData.items():
        teams[teamData[key]["team"]].append(key)
        if not (teamData[key]["isBot"]):
            print("Not a bot")
    print(client)
    for member in client.get_guild(834779618694791218).members:
        if(not member.bot):
            if(teamData[member.name]["captain"] == True):
                role = discord.utils.get(member.guild.roles, name="Captain")
                await member.add_roles(role)
    # await client.get_channel(client_id).send("Welcome to the DnD bot!")

#TO-DO:
#add a -score command
#   update: this is hard because the actual score isn't actually calculated until the end of the round
#prevent the user from entering in commands if the game is already going (if Gryffindor is not one of the teams in the current match)
#have a pause before the start of each "inning" (before the first play of each inning starts)
#add flavor text (say who exactly is injured at the start of each round, etc., etc.)
#have opposing teams burn rerolls automatically
#fully flesh out the documentation, the -help menu and refactor the code
#add arguments to all of the atrribute commands
#12/10/2021 BE WARY OF REFACTORING
#12/11/2021 Make sure that the sub method actually works
#12/16/2021 Make add more user friendly. Make add it's own seperate function and make sure that search_for_sub calls that function

async def set(channel, message, role, sub=False):
    player = message[3]
    if player not in teamData:
        await channel.send("Could not find player in database")
        return
    if player in teamData and (teamData[player]["injured"] == True or teamData[player]["critically_injured"] == True):
        await channel.send("Cannot add an injured player to the roster!")
        return
    team = teamData[player]["team"]
    print(team)
    if team not in team_rosters:
        await channel.send("Sorry, I didn't recognize the team name")
        return
    if role == None and teamData[message.author.name]["team"] != teamData[player]["team"]:
        await channel.send(player + " is not on your team!")
        return
    position = message[2]
    position_to_set = position
    specific_cases= ["Beater1", "Beater2", "Chaser1", "Chaser2", "Chaser3"]
    if(position in specific_cases):
        position_to_set = position[:-1]

    if(teamData[player]["position"] != position_to_set):
        await channel.send(player + " is not a " + position + "!")
        return

    if position not in team_rosters[team]:
        await channel.send("Invalid position name. Try using -help -set for more info")
        return

    team_rosters[team][position] = player
    if(sub):
        await channel.send("Subbed " + position + " for team " + team + " to " + player)
        current_player = team_rosters[team][position]
        team_rosters[team][position] = player
        for i in range(index_i, len(team_A_rolls)):
            if(team_A_rolls[i][0] == current_player):
                #reroll
                tuple = (player, random.randint(1, 12) + teamData[player]["rank"])
                team_A_rolls[i] = tuple
        print("Current player")
        print(current_player)
        if(team_B_rolls[0][0] == current_player and position == "Keeper"):
            for i in range(index_i, len(team_B_rolls)):
                 team_B_rolls[i] = random.randint(1, 12) + teamData[player]["rank"]
        return
    if(channel != None):
        await channel.send("Set " + position + " for team " + team + " to " + player)

async def search_for_param(param, message, channel):
    if (len(message) != 2):
        await channel.send("Invalid number of arguments")
        return
    if(message[1] not in teamData):
        await channel.send("Could not find player in database")
        return
    await channel.send(teamData[message[1]][param])

async def clear():
    for key, value in teamData.items():
        teamData[key]["xp"] = 0
        teamData[key]["rank"] = 0

async def set_param(channel, player, key, value):
    if player in teamData:
        bool_vars = ["captain", "injured", "critically_injured", "isBot"]
        int_vars = ["jersey", "rank", "xp"]
        if(key in bool_vars):
            teamData[player][key] = eval(value)
        elif(key in int_vars):
            teamData[player][key] = int(value)
        else:
            if key in teamData[player]:
                teamData[player][key] = value
            else:
                await channel.send("Not a valid attribute")
        print(teamData[player][key])
    else:
        await channel.send("Player not found in database")

async def add_player(message):
    params = message.split(' ')
    # AttributeError: 'list' object has no attribute 'split'
    params = params[1:]
    #do special processing of the string
    required_args = ["name", "position", "team", "captain"]
    if params[0] in teamData:
        return "Player already in file"
    teamData[params[0]] = {}
    for j in range(len(required_args)-1):
        l = len(required_args[j])
        post_index = message.find(required_args[j+1])
        current_index = message.find(required_args[j])
        subst = message[current_index+l+1:post_index-1]
        print("Subst:", subst)
        if(subst == "True" or subst == "False"):
            teamData[params[0]][required_args[j]] = eval(subst)
        else:
            teamData[params[0]][required_args[j]] = subst
    post_index = message.find(required_args[len(required_args)-1])
    l = len(required_args[len(required_args)-1])
    print(message[post_index+l+1:])
    subst = message[post_index+l+1:]
    if(subst == "True" or subst == "False"):
        teamData[params[0]][required_args[len(required_args)-1]] = eval(subst)
    else:
        teamData[params[0]][required_args[len(required_args)-1]] = subst
    teamData[params[0]]["rank"] = 0
    teamData[params[0]]["xp"] = 0
    teamData[params[0]]["critically_injured"] = False
    teamData[params[0]]["injured"] = False
    teamData[params[0]]["isBot"] = True
    #add defaults for other params too
    teams[teamData[params[0]]["team"]].append(teamData[params[0]])
    return "Success"

async def auto_populate(team_to_fill):
    if team_to_fill in team_list:
        for key, value in teamData.items():
            position = teamData[key]["position"]
            team = teamData[key]["team"]
            if team_to_fill.find(team) != -1:
                #prevent same player from being assigned to the same team twice
                bool = next((team[0] for team in team_rosters.items() for t in team[1].items() if t[1] == key), None)
                print(bool)
                if (bool == None):
                    if position == "Beater":
                        if team_rosters[team_to_fill]["Beater1"] == None:
                            team_rosters[team_to_fill]["Beater1"] = key
                        elif team_rosters[team_to_fill]["Beater2"] == None:
                            team_rosters[team_to_fill]["Beater2"] = key 
                    elif position == "Chaser":
                        if team_rosters[team_to_fill]["Chaser1"] == None:
                            team_rosters[team_to_fill]["Chaser1"] = key
                        elif team_rosters[team_to_fill]["Chaser2"] == None:
                            team_rosters[team_to_fill]["Chaser2"] = key
                        elif team_rosters[team_to_fill]["Chaser3"] == None:
                            team_rosters[team_to_fill]["Chaser3"] = key
                    else:
                        if position == "Keeper" and team_rosters[team_to_fill]["Keeper"] == None:
                            team_rosters[team_to_fill]["Keeper"] = key
                        if position == "Seeker" and team_rosters[team_to_fill]["Seeker"] == None:
                            team_rosters[team_to_fill]["Seeker"] = key
        #TO-DO: finish this
        captains = await find_team_captain(team_to_fill)
        print(team_rosters)
        if(len(captains) != 0): #more complicated than I was hoping it would be
            captain = captains[0]
            position = teamData[captain]["position"]


async def fill_roster_message(channel, team):
    team_roster_invalid = True
    for key, value in team_rosters[team].items():
        if value == None:
            team_roster_invalid = True
            continue
    team_roster_invalid = False
    return team_roster_invalid

async def displayRoster(channel, team):
    return_message = team
    for key, value in team_rosters[team].items():
        return_message += "\n" + key + "\t" + str(value)
    print(return_message)
    await channel.send(return_message)

async def autogen_roster(args):
    file_name = args[1]
    for arg in args[2:]:
        print(arg)
        if arg not in teamData:
            return -1
    roster = {}
    positions = ["Chaser1", "Chaser2", "Chaser3", "Beater1", "Beater2", "Keeper", "Seeker"]
    current_player = 2
    while(len(positions) > 0):
        rn = random.randint(0, len(positions)-1)
        print(rn)
        print(positions[rn])
        roster[positions[rn]] = args[current_player]
        positions.pop(rn)
        print("len(positions)", len(positions))
        current_player += 1

    pass
    print(roster)
    with open(file_name, 'w', encoding='utf-8') as file:
        json.dump(roster, file)
    print("Saved successfully")

async def start_practice():
    pass

async def gen_roster(args):
    file_name = args[1]
    for arg in args[2:]:
        if arg not in teamData:
            return -1
    roster = {}
    positions = ["Chaser1", "Chaser2", "Chaser3", "Beater1", "Beater2", "Keeper", "Seeker"]
    for pos in positions:
        roster[pos] = None
    
    for arg in args[2:]:
        position = teamData[arg]["position"]
        if position == "Chaser" or position == "Keeper":
            pass
        print(position)

async def list_temp_roster(channel):
    global temp_rosters
    for key, value in temp_rosters.items():
        message = "Team " + key + "\n"
        for k, v in value.items():
            message += k + "\t" + v + "\n"
        await channel.send(message)
async def gen_practice_roster(args):
    pass

async def get_players(team_name):
    pass

async def set_team_roster(team, practice):
    global temp_rosters
    #double check that players are actually on the team
    print(temp_rosters)
    for key, value in temp_rosters.items():
        for k, v in value.items():
            if(v not in teams[team]):
                return "{} not in {}".format(v, team)
    team_rosters[team] = temp_rosters[practice]
    return "Success"
@client.event
async def on_message(message):
    global currentMatch
    print(currentMatch)
    if(currentMatch != None):
        print(currentMatch.isHeadless())
    if message.author.bot:
        print("This should be called")
        return
    #feed the input directly to an asynchronous method designed to handle input for when the game is actually started
    if(currentMatch != None and not currentMatch.isHeadless()):
        print("Answer")
        # print(message.content.find("-stop "))
        # print(message.content.find("-stop ") != -1)
        # if(message.content.find("-stop ") != 1):
        #     print(type(message.content))
        #     print("Don't call this")
        #     await message.channel.send("Cannot send messages while a game is going on")
        print(message.content)
        print(message.content.find("continue") != -1)
        print("continue" in message.content)
        if message.content.find("continue") != -1:
            print("What")
            await currentMatch.unpause()
            return
    if(message.content.find("-set ") != -1): #valid command makes 4 arguments
    #-set -p [position_name] [player_name]
        generator = (entry for entry in message.author.roles if entry.name=="Admin")
        role = next(generator, None)
        if(teamData[message.author.name]["captain"] == True or role != None):
            m = message.content.split()
            if(len(m) != 4 or m[1] != "-p"):
                await message.channel.send("Invalid command. Try using -help -set for more info")
                return
            await set(message.channel, m, role)
        else:
            await message.channel.send("Can't use the -set command unless you're a captain for an admin")
    elif message.content.find("-help") != -1: 
        await message.channel.send(help_string)
    elif message.content.find("-name ") != -1:
        m = message.content.split()
        await search_for_param("name", m, message.channel)

    elif message.content.find("-position ") != -1:
        m = message.content.split()
        await search_for_param("position", m, message.channel)

    elif message.content.find("-year ") != -1:
        m = message.content.split()
        await search_for_param("year", m, message.channel)

    elif message.content.find("-rank ") != -1:
        m = message.content.split()
        await search_for_param("rank", m, message.channel)

    elif message.content.find("-xp ") != -1:
        m = message.content.split()
        await search_for_param("xp", m, message.channel)

    elif message.content.find("-score ") != -1:
        if(not gameStarted):
            await message.channel.send("No game is ongoing")
            return
        await message.channel.send("Score is " + team_a + ": " + str(scores[team_a]) + ", " +  team_b + ": " + str(scores[team_b]))
        
    elif message.content.find("-captain ") != -1:
        m = message.content.split()
        if(len(m) != 2):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        team = m[1]
        captains = await find_team_captain(team)
        if(len(captains) > 0):
            await message.channel.send("The captain of " + str(team) + " is " + captains[0])
        else:
            await message.channel.send(str(team) + " does not have a captain!")

    elif message.content.find("-write ") != -1: #helper function for quickly writing extra parameters to the json file without extra hassle
        m = message.content.split()
        if(len(m) != 4):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        param = m[1]
        default_value = m[2]
        typeVar = m[3]
        if(typeVar == "boolean"):
            default_value = eval(default_value)
        elif(typeVar == "int"):
            default_value = int(default_value)
        await write_params(param, default_value, message.channel)

    elif message.content.find("-roster ") != -1:
        m = message.content.split()
        if(len(m) != 2):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        team = m[1]
        if team not in team_rosters:
            await message.channel.send("Didn't recognize the team name")
            return
        await displayRoster(message.channel, team)

    elif message.content.find("-autopop ") != -1: #autopopulate command takes one argument
        if(currentMatch != None):
            return
        m = message.content.split()
        if(len(m) != 2):
            await message.channel.send("Incorrect number of arguments")
            return
        team = m[1]
        await auto_populate(team)
        await displayRoster(message.channel, team)
        await message.channel.send("Use the -set command to make any changes to the roster")

    elif message.content.find("-start ") != -1: #have start take one to two arguments
        #if there is one argument in the entry, assume that the game is between the team provided and Gryffindor
        m = message.content.split()
        if(currentMatch != None):
            return
        if(len(m) != 3):
            await message.channel.send("Invalid number of arguments")
            return
        else:
            teamA = m[1]
            teamB = m[2]
            if teamA not in teams:
                await message.channel.send(teamA + " not a valid team name")
                return
            if teamB not in teams:
                await message.channel.send(teamB + " not a valid team name")
                return
            for key, value in team_rosters[teamA].items():
                if value == None:
                    await message.channel.send("Invalid roster for " + teamA)
                    return
            for key, value in team_rosters[teamB].items():
                if value == None:
                    await message.channel.send("Invalid roster for " + teamB)
                    return
            await message.channel.send("Match is ready to start!")
            gameStarted = True
            if teamA == "Gryffindor" or teamB == "Gryffindor":
                currentMatch = Match(teamA, teamB, team_rosters, message.channel, flavorText, teamData)
                await currentMatch.start_match()
            else:
                await start_match_headless(message.channel, teamA, teamB)
    elif message.content.find("-start_practice ") != -1:
        print("Start practice")
        await start_practice()
    elif message.content.find("-add ") != -1:
        #currently, this code splits the name in half which is not good
        required_args = [" name", " position", " team", " captain"]
        for arg in required_args:
            if(message.content.find(arg) == -1):
                await message.channel.send(arg + " is required")
                return
        result = await add_player(message.content)
        await message.channel.send(result)

    elif message.content.find("-save") != -1:
        await save(message.channel)

    elif message.content.find("-sub ") != -1: #similar in principle to sub but sub subs in a character who already is in the game
        print(gameStarted)
        if not (gameStarted):
            await message.channel.send("Can't sub in anyone right now. Consider using -set instead")
            return
        generator = (entry for entry in message.author.roles if entry.name=="Admin")
        role = next(generator, None)
        if(teamData[message.author.name]["captain"] == True or role != None):
            m = message.content.split()
            print(m)
            if(len(m) < 4):
                await message.channel.send("Invalid command. Try using -help -set for more info")
                return
            if(m[1] == "-p"):
                await set(message.channel, m, role, sub=True)
        else:
            await message.channel.send("Can't use the -set command unless you're a captain for an admin")
    elif message.content.find("-reroll") != -1:
        await reroll(message.channel)
    elif message.content.find("-search") != -1:
        m = message.content.split()
        if(len(m) != 3):
            await message.channel.send("Invalid number of arguments")
            return
        team = m[1]
        if team not in team_rosters:
            await message.channel.send("Sorry, I didn't recognize the team name")
            return
        pos = m[2]
        if (pos != "Chaser" and pos != "Beater" and pos != "Keeper" and pos != "Seeker"):
            await message.channel.send("Invalid position name")
            return
        for key, value in teamData.items():
            if(teamData[key]["team"] == team and teamData[key]["position"] == pos):
                if(teamData[key]["critically_injured"] == True):
                    await message.channel.send(key + " (critically injured)")
                elif(teamData[key]["injured"] == True):
                    await message.channel.send(key + " (injured)")
                else:
                    await message.channel.send(key)
    elif message.content.find("-clear") != -1: #clears rank and xp
        await clear()
    elif message.content.find("-pause") != -1:
        if(gameStarted):
            gameStarted = False
            await message.channel.send("Game stopped")
        else:
            await message.channel.send("No game in progress")
    elif message.content.find("-load_roster") != -1:
        m = message.content.split()
        print(m)
        if(len(m) != 3):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        roster = await load_roster_from_file(m[1], m[2])
    elif message.content.find("-set_param") != -1:
        m = message.content.split()
        if(len(m) != 4):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        await set_param(message.channel, m[1], m[2], m[3])
    elif message.content.find("-autogen_roster") != -1: #useful for when we want to add a lot of players to an example file quickly
        m = message.content.split()
        if(len(m) != 9):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        result = await autogen_roster(m)
        if(result != -1):
            await message.channel.send("Saved successfully")
        else:
            await message.channel.send("One or more of the players provided could not be recognized")
    elif message.content.find("-gen_roster") != -1: #used for creating a varsity roster
        #functions in very much the same way as above, but with the positions being already defined
        m = message.content.split()
        if(len(m) != 9):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        result = await gen_roster(m)
    elif message.content.find("-gen_practice_roster") != -1:
        m = message.content.split()
        if(len(m) < 2 and len(m) > 5):
            await message.channel.send("Couldn't recognize that command. Try -help")
        result = await gen_practice_roster(m)
        pass
    elif message.content.find("-list_roster") != -1:
        await list_temp_roster(message.channel)
        pass
    elif message.content.find("-load_practice_roster") != -1:
        pass
    elif message.content.find("-replace_roster") != -1:
        pass
    elif(message.content.find("-set_roster") != -1):
        m = message.content.split()
        #first arg - team name
        #second arg - roster name
        if(len(m) != 3):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        response = await set_team_roster(m[1], m[2])
        await message.channel.send(response)
        pass
    elif(message.content.find("-list_players") != -1):
        m = message.content.split()
        #first arg - team name
        if(len(m) != 2):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        response = await get_players(m[1])
        await message.channel.send(response)
        pass
    else:
        await message.channel.send("Couldn't recognize that command. Try -help")

client.run(os.getenv("TOKEN"))