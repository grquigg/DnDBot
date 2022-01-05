import discord
from discord import team
from discord.ext import commands
import os
import json
from enum import Enum
import random
import asyncio
from discord import message
from dotenv import load_dotenv

load_dotenv()
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
bots = commands.Bot(command_prefix='!')

class MatchState(Enum):
    TEAM_A_TURN = 1
    TEAM_B_TURN = 2


# def has_role(role_name, member):
default_path = "./examplefile.json"
client_id = int(os.getenv("CLIENT_ID"))

async def start_match_headless(channel, teamA, teamB):
    global gameStarted
    gameStarted = True
    global num_rounds
    global teamA_score
    global teamB_score
    global scores
    scores = {}
    scores[teamA] = 0
    scores[teamB] = 0
    A = random.randint(1, 20)
    B = random.randint(1, 20)
    num_rounds = 1
    first_team = ""
    first_team = ""
    second_team = ""
    coin = random.randint(0, 1)
    if(coin == 0):
        first_team = teamA
        second_team = teamB
    else:
        first_team = teamB
        second_team = teamA
    for i in range(num_rounds):
        await run_round_headless(first_team, second_team)
        await run_round_headless(second_team, first_team)
    teamA_rolls = 0
    teamB_rolls = 0 
    for j in range(3):
        teamA_rolls += random.randint(1, 6)
        teamB_rolls += random.randint(1, 6)
    teamA_rolls += teamData[team_rosters[first_team]["Seeker"]]["rank"]
    teamB_rolls += teamData[team_rosters[second_team]["Seeker"]]["rank"]

    if(teamData[team_rosters[first_team]["Seeker"]]["injured"]):
        teamA_rolls -= 1
    if(teamData[team_rosters[second_team]["Seeker"]]["injured"]):
        teamB_rolls -= 1

    teamData[team_rosters[first_team]["Seeker"]]["xp"] += (teamA_rolls * 10)
    teamData[team_rosters[second_team]["Seeker"]]["xp"] += (teamB_rolls * 10)
    
    if(teamA_rolls > teamB_rolls):
        scores[teamA] += 150
        seeker = teamData[team_rosters[first_team]["Seeker"]]["name"]
        teamData[team_rosters[first_team]["Seeker"]]["xp"] += 150
    elif (teamB_rolls > teamA_rolls):
        scores[teamB] += 150
        seeker = teamData[team_rosters[second_team]["Seeker"]]["name"]
        teamData[team_rosters[second_team]["Seeker"]]["xp"] += 150
    if(scores[teamA] > scores[teamB]):
        await channel.send(first_team + " wins!")
    elif(scores[teamB] > scores[teamA]):
        await channel.send(second_team + " wins!")
    else:
        await channel.send("The score is a tie, so " + second_team + " wins!")
    await channel.send("Score is " + str(first_team) + ": " + str(scores[teamA]) + ", " + str(second_team) + ": " + str(scores[teamB]))
    gameStarted = False
    await clean_up()

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

async def start_match(channel, teamA, teamB):
    global num_rounds
    global gameStarted
    gameStarted = True
    A = random.randint(1, 20)
    B = random.randint(1, 20)
    num_rounds = random.randint(1, 12)
    global scores
    scores = {}
    scores[teamA] = 0
    scores[teamB] = 0
    first_team = ""
    second_team = ""
    coin = random.randint(0, 1)
    if(coin == 0):
        await channel.send(teamA + " will be on the offensive first")
        first_team = teamA
        second_team = teamB
    else:
        await channel.send(teamB + " will be on the offensive first")
        first_team = teamB
        second_team = teamA
    for i in range(num_rounds):
        await run_round(first_team, second_team, channel)
        await channel.send("Now it is " + second_team + "'s turn to be on the offense")
        await channel.send("Type 'continue' to continue")
        while(control_sequence == False):
            await asyncio.sleep(1)
        await run_round(second_team, first_team, channel)
        await channel.send("Score is " + first_team + ": " + str(scores[teamA]) + ", " +  second_team + ": " + str(scores[teamB]))
    teamA_rolls = 0
    teamB_rolls = 0 
    for j in range(3):
        teamA_rolls += random.randint(1, 6)
        teamB_rolls += random.randint(1, 6)
    teamA_rolls += teamData[team_rosters[first_team]["Seeker"]]["rank"]
    teamB_rolls += teamData[team_rosters[second_team]["Seeker"]]["rank"]

    if(teamData[team_rosters[first_team]["Seeker"]]["injured"]):
        teamA_rolls -= 1
    if(teamData[team_rosters[second_team]["Seeker"]]["injured"]):
        teamB_rolls -= 1

    teamData[team_rosters[first_team]["Seeker"]]["xp"] += (teamA_rolls * 10)
    teamData[team_rosters[second_team]["Seeker"]]["xp"] += (teamB_rolls * 10)
    
    if(teamA_rolls > teamB_rolls):
        scores[teamA] += 150
        seeker = teamData[team_rosters[first_team]["Seeker"]]["name"]
        teamData[team_rosters[first_team]["Seeker"]]["xp"] += 150
        await channel.send(seeker + " has caught the Snitch!")
    elif (teamB_rolls > teamA_rolls):
        scores[teamB] += 150
        seeker = teamData[team_rosters[second_team]["Seeker"]]["name"]
        teamData[team_rosters[second_team]["Seeker"]]["xp"] += 150
        await channel.send(seeker + " has caught the Snitch!")
    await check_for_level_up(teamData[team_rosters[first_team]["Seeker"]], channel)
    await check_for_level_up(teamData[team_rosters[second_team]["Seeker"]], channel)
    await channel.send("Final score is " + first_team + ": " + str(scores[teamA]) + ", " +  second_team + ": " + str(scores[teamB]))
    if(scores[teamA] > scores[teamB]):
        await channel.send(first_team + " wins!")
    elif(scores[teamB] > scores[teamA]):
        await channel.send(second_team + " wins!")
    else:
        await channel.send("The score is a tie, so " + second_team + " wins!")
    gameStarted = False
    await clean_up()

async def check_for_level_up(player, channel):
    if(player["xp"] > 100 and player["rank"] < 1):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 1!")
        player["rank"] = 1
    elif(player["xp"] > 250 and player["rank"] < 2):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 2!")
        player["rank"] = 2
    elif(player["xp"] > 450 and player["rank"] < 3):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 3!")
        player["rank"] = 3
    elif(player["xp"] > 700 and player["rank"] < 4):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 4!")
        player["rank"] = 4
    elif(player["xp"] > 1000 and player["rank"] < 5):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 5!")
        player["rank"] = 5
    elif(player["xp"] > 1400 and player["rank"] < 6):
        if(channel != None):
            await channel.send(str(player["name"]) + " has leveled up to Rank 6!")
        player["rank"] = 6

#TO-DO: Have the game be more interactive. Choose who the beater goes after

async def search_for_sub(team, position):
    new_player = False
    if("Chaser" in position[0]):
        chaser_list = [] #players that are already in the current match
        if(position[0] == "Chaser1"):
            chaser_list.append(team_rosters[team]["Chaser2"])
            chaser_list.append(team_rosters[team]["Chaser3"])
        elif(position[0] == "Chaser2"):
            chaser_list.append(team_rosters[team]["Chaser1"])
            chaser_list.append(team_rosters[team]["Chaser3"])
        elif(position[0] == "Chaser3"):
            chaser_list.append(team_rosters[team]["Chaser1"])
            chaser_list.append(team_rosters[team]["Chaser2"])
        replacement = ""
        name = ""
        pos = ""
        for char in teams[team]:
            if (char not in chaser_list and not teamData[char]["critically_injured"]):
                if(teamData[char]["position"] == "Chaser"):
                    replacement = char
        if(replacement == ""):
            list = [i for i in teams[team] if teamData[i]["position"] == "Chaser"]
            replacement = "chaser_" + team + "#" + str(len(list))
            name = "Chaser_ " + team + str(len(list))
            teams[team].append(replacement)
            new_player = True
        pos = "Chaser"
    elif("Beater" in position[0]):
        beater_list = []
        if(position[0] == "Beater1"):
            beater_list.append(team_rosters[team]["Beater2"])
        elif(position[0] == "Beater2"):
            beater_list.append(team_rosters[team]["Beater1"])
        replacement = ""
        for char in teams[team]:
            if (not teamData[char]["critically_injured"]):
                if(teamData[char]["position"] == "Beater"):
                    replacement = char

        if(replacement == ""):
            list = [i for i in teams[team] if teamData[i]["position"] == "Beater"]
            replacement = "beater_" + team + "#" + str(len(list))
            name = "Beater_ " + team + str(len(list))
            teams[team].append(replacement)
            new_player = True
        pos = "Beater"
    elif("Seeker" in position[0]):
        replacement = ""
        for char in teams[team]:
            if (not teamData[char]["critically_injured"]):
                if(teamData[char]["position"] == "Seeker"):
                    replacement = char

        if(replacement == ""):
            list = [i for i in teams[team] if teamData[i]["position"] == "Seeker"]
            replacement = "seeker_" + team + "#" + str(len(list))
            name = "Seeker_ " + team + str(len(list))
            teams[team].append(replacement)
            new_player = True
        pos = "Seeker"
    if(new_player):
        args = [replacement, "name", name, "position", pos, "team", team]
        await add_player(args)
    print("Player to sub in: " + replacement)
    team_rosters[team][position[0]] = replacement
    print(team_rosters[team])

async def reroll(channel):
    global team_rerolls
    global score
    if(team_rerolls > 0):
        player = team_A_rolls[index_i][0]
        rerollA = random.randint(1, 12) + teamData[player]["rank"]
        if(teamData[player]["injured"]):
            rerollA -= 1
        rerollB = random.randint(1, 12) + teamData[team_rosters[team_b]["Keeper"]]["rank"]
        if(teamData[team_rosters[team_b]["Keeper"]]):
            rerollB -= 1
        team_A_rolls[index_i] = (player, rerollA + team_A_rolls[index_i][1])
        team_B_rolls[index_i] = team_B_rolls[index_i] + rerollB
        if (team_A_rolls[index_i][1] > team_B_rolls[index_i]):
            teamData[team_A_rolls[index_i][0]]["xp"] += 25
            await channel.send(teamData[team_A_rolls[index_i][0]]["name"] + " has scored a goal")
            await check_for_level_up(teamData[team_A_rolls[index_i][0]], channel)
            scores[team_a] += 30
        elif(team_A_rolls[index_i][1] < team_B_rolls[index_i]):
            if(team_B_rolls[index_i] - team_A_rolls[index_i][1] <= 2):
                await channel.send(teamData[team_A_rolls[index_i][0]]["name"] + " almost managed to score a goal but " + teamData[team_rosters[team_b]["Keeper"]]["name"] + " blocked it at the last second!")
            else:
                await channel.send(teamData[team_rosters[team_b]["Keeper"]]["name"] + " has blocked " + teamData[team_A_rolls[index_i][0]]["name"] + " from scoring")
            teamData[team_A_rolls[index_i][0]]["xp"] += 5
            keeper = team_rosters[team_b]["Keeper"]
            teamData[keeper]["xp"] += 10
            await check_for_level_up(teamData[team_A_rolls[index_i][0]], channel)
            await check_for_level_up(teamData[keeper], channel)
        team_rerolls -= 1
        await channel.send(str(team_rerolls) + " rerolls left")
        await channel.send("Type 'continue' to continue")
    else:
        await channel.send("No more rerolls left")

async def beater_turn(beater, channel, a, b):
    print("Beater turn")
    roll = random.randint(1, 12) + beater["rank"]
    if (beater["injured"]):
        roll =- 1
    if(roll > 8):
        if(channel != None):
            await channel.send(beater["name"] + " tried to hit someone but missed")
    elif(roll >= 8 or roll < 12):
        min_roll = random.randint(1, 12)
        hit_player = 0
        for int in range(6):
            comparison_roll = random.randint(1, 12)
            if(min_roll > comparison_roll):
                min_roll = comparison_roll
                hit_player = int
        hit = list(team_rosters[b].items())[hit_player]
        if(teamData[hit[1]]["injured"] == True):
            if(channel != None):
                await channel.send(beater["name"] + " hit " + str(teamData[hit[1]]["name"]) + " when they were they were already injured!")
                await channel.send(str(teamData[hit[1]]["name"]) + " was knocked unconscious and cannot play")
            teamData[hit[1]]["critically_injured"] = True
            if(channel != None):
                await channel.send("Need to substitute for the position " + str(hit[0]))
            team_rosters[b][hit[0]] = None
            while(team_rosters[b][hit[0]] == None):
                if(channel == None or b != "Gryffindor"):
                    print("Call search for sub")
                    await search_for_sub(b, hit)
                await asyncio.sleep(1)
        else:
            teamData[hit[1]]["injured"] = True
            if(channel != None):
                await channel.send(beater["name"] + " hit " + str(teamData[hit[1]]["name"]) + ", minorly injuring them")
                await channel.send(str(teamData[hit[1]]["name"]) + " is now injured and will roll with disadvantage")

        beater["xp"] += 50
        await check_for_level_up(beater, channel)
    elif(roll >= 12):
        min_roll = random.randint(1, 12)
        hit_player = 0
        for int in range(6):
            comparison_roll = random.randint(1, 12)
            if(min_roll > comparison_roll):
                min_roll = comparison_roll
                hit_player = int
        hit = list(team_rosters[b].items())[hit_player]
        if(channel != None):
            await channel.send(beater["name"] + " hit " + str(teamData[hit[1]]["name"]) + " and landed a critical hit!")
        beater["xp"] += 100
        await check_for_level_up(beater, channel)
        team_rosters[b][hit[0]] = None
        if (channel != None):
            await channel.send("Need to substitute for the position " + str(hit[0]))
        while(team_rosters[b][hit[0]] == None):
            if(channel != None or b != "Gryffindor"):
                await search_for_sub(b, hit)
            await asyncio.sleep(1)

async def clean_up():
    global teamData
    for key, value in teamData.items():
        if(teamData[key]["injured"]):
            teamData[key]["injured"] = False
        if(teamData[key]["critically_injured"]):
            teamData[key]["critically_injured"] = False
            teamData[key]["injured"] = True
            
async def run_round(a, b, channel):
    global control_sequence
    global team_A_rolls
    global team_B_rolls
    global index_i
    global team_rerolls
    global team_a
    global team_b
    global quaffle_possession
    quaffle_possession = "" #keeps track of who has the quaffle
    last_roll_success = False #keeps track of whether the last roll was a success or not (used for flavor text)
    team_a = a
    team_b = b
    team_rerolls = 3
    control_sequence = False
    team_rolls = []
    for j in range(3):
        roll = random.randint(1, 12)
        team_rolls.append(roll)

    maxRoll = max(team_rolls)
    team_A_rolls = []
    team_B_rolls = []
    beater_rolls = []
    for int in range(2):
        beater_rolls.append(random.randint(0, maxRoll-1))

    for k in range(maxRoll):
        r = ()
        if(k % 3 == 0):
            chaser = team_rosters[a]["Chaser1"]
        elif(k % 3 == 1):
            chaser = team_rosters[a]["Chaser2"]
        else:
            chaser = team_rosters[a]["Chaser3"]
        r = (chaser, (random.randint(1, 12) + teamData[chaser]["rank"]))
        if(teamData[chaser]["injured"]):
            roll = r[1]
            r = (chaser, roll - 1)

        team_A_rolls.append(r)
        keeper = team_rosters[b]["Keeper"]
        team_B_rolls.append(random.randint(1, 12) + teamData[keeper]["rank"])

        if(teamData[keeper]["injured"]):
            team_B_rolls[k] -= 1
            
    team_A_rolls.sort(reverse=True, key = lambda x: x[1])
    team_B_rolls.sort(reverse=True)
    #have to keep track of the index 
    for x in range(maxRoll):
        print("Turn " + str(x))
        index_i = x
        if(beater_rolls[0] == x):
            beater = teamData[team_rosters[a]["Beater1"]]
            await beater_turn(beater, channel, a, b)

        if(beater_rolls[1] == x):
            beater = teamData[team_rosters[a]["Beater2"]]
            await beater_turn(beater, channel, a, b)

        if (team_A_rolls[x][1] > team_B_rolls[x]):

            teamData[team_A_rolls[x][0]]["xp"] += 25
            if(quaffle_possession == team_A_rolls[x][0]):
                #there should be a distinct move name for this
                #also if this happens more than once, then stop it
                #there should be a roll for "interception"
                await channel.send(teamData[team_A_rolls[x][0]]["name"] + " somehow manages to score again!")
            else:
                if(quaffle_possession != ""):
                    await channel.send(teamData[quaffle_possession]["name"] + " passes the quaffle to " + teamData[team_A_rolls[x][0]]["name"]
                    + " and " + teamData[team_A_rolls[x][0]]["name"] + " scores a goal!")
                else:
                    await channel.send(teamData[team_A_rolls[x][0]]["name"] + " scores a goal!") 
            await check_for_level_up(teamData[team_A_rolls[x][0]], channel)
            scores[team_a] += 30
            quaffle_possession = team_A_rolls[x][0]
            last_roll_success = True
        elif(team_A_rolls[x][1] < team_B_rolls[x]):
            if(team_B_rolls[x] - team_A_rolls[x][1] <= 2):
                await channel.send(teamData[team_A_rolls[x][0]]["name"] + " almost managed to score a goal but " + teamData[keeper]["name"] + " blocked it at the last second!")
                quaffle_possession = team_A_rolls[x][0]
                if(a != "Gryffindor"):
                    print("Reroll")
                    await reroll(channel)
            else:
                await channel.send(teamData[keeper]["name"] + " has blocked " + teamData[team_A_rolls[x][0]]["name"] + " from scoring")
                quaffle_possession = team_A_rolls[x][0]
            last_roll_success = False
            teamData[team_A_rolls[x][0]]["xp"] += 5
            keeper = team_rosters[b]["Keeper"]
            teamData[keeper]["xp"] += 10
            await check_for_level_up(teamData[team_A_rolls[x][0]], channel)
            await check_for_level_up(teamData[keeper], channel)
        else:
            continue
        await channel.send("Type 'continue' to continue")
        while(control_sequence == False):
            await asyncio.sleep(1)
        control_sequence = False
    await channel.send(teamData[quaffle_possession]["name"] + " tries to score but the Keeper " + teamData[team_rosters[b]["Keeper"]]["name"] + " blocks it and takes possession of it.")

async def run_round_headless(teamA, teamB):
    global team_A_rolls
    global team_B_rolls
    team_a = teamA
    team_b = teamB   
    global scores
    team_rolls = []
    for j in range(3):
        roll = random.randint(1, 12)
        team_rolls.append(roll)

    maxRoll = max(team_rolls)

    team_A_rolls = []
    team_B_rolls = []
    beater_rolls = []
    for int in range(2):
        beater_rolls.append(random.randint(0, maxRoll))
    for k in range(maxRoll):
        if(k % 3 == 0):
            chaser = team_rosters[team_a]["Chaser1"]
        elif(k % 3 == 1):
            chaser = team_rosters[team_a]["Chaser2"]
        else:
            chaser = team_rosters[team_a]["Chaser3"]

        r = (chaser, (random.randint(1, 12) + teamData[chaser]["rank"]))
        if(teamData[chaser]["injured"]):
            roll = r[1]
            r = (chaser, roll - 1)
        team_A_rolls.append(r)
        keeper = team_rosters[team_b]["Keeper"]
        team_B_rolls.append(random.randint(1, 12) + teamData[keeper]["rank"])

        if(teamData[keeper]["injured"]):
            print("keeper is injured")
            team_B_rolls[k] -= 1
            
    team_A_rolls.sort(reverse=True, key = lambda x: x[1])
    team_B_rolls.sort(reverse=True)

    #have to keep track of the index 
    for x in range(maxRoll):
        index_i = x
        if(beater_rolls[0] == x):
            print("beater turn")
            beater = teamData[team_rosters[team_a]["Beater1"]]
            await beater_turn(beater, None, team_a, team_b)

        if(beater_rolls[1] == x):
            beater = teamData[team_rosters[team_a]["Beater2"]]
            await beater_turn(beater, None, team_a, team_b)

        if (team_A_rolls[x][1] > team_B_rolls[x]):

            teamData[team_A_rolls[x][0]]["xp"] += 25
            await check_for_level_up(teamData[team_A_rolls[x][0]], None)
            scores[team_a] += 30
        elif(team_A_rolls[x][1] < team_B_rolls[x]):
            teamData[team_A_rolls[x][0]]["xp"] += 5
            keeper = team_rosters[team_b]["Keeper"]
            teamData[keeper]["xp"] += 10
            await check_for_level_up(teamData[team_A_rolls[x][0]], None)
            await check_for_level_up(teamData[keeper], None)
        else:
            continue

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    global DEVELOPMENT_MODE
    global teamData
    global gameType
    global gameStarted
    global matchState
    global control_sequence
    global teams
    global team_rosters
    global teamA_score
    global teamB_score
    global team_list
    global help_string
    team_list = ["Gryffindor", "Ravenclaw", "Slytherin", "Hufflepuff"]
    gameStarted = False
    DEVELOPMENT_MODE = True
    teams = {}
    team_rosters = {}
    teamA_score = 0
    teamB_score = 0
    with open(default_path, "r", encoding="utf8") as file:
        for line in file:
            teamData = json.loads(line)
    helper = []
    with open("help.txt", "r", encoding="utf8") as help:
        for line in help:
            helper.append(line)
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
        
    for member in client.get_channel(client_id).members:
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

async def add_player(params):
    teamData[params[0]] = {}
    for i in range(1, len(params), 2):
        if(params[i+1] == "True" or params[i+1] == "False"):
            teamData[params[0]][params[i]] = eval(params[i+1])
        else:
            teamData[params[0]][params[i]] = params[i+1]
    teamData[params[0]]["rank"] = 0
    teamData[params[0]]["xp"] = 0
    teamData[params[0]]["critically_injured"] = False
    teamData[params[0]]["injured"] = False
    teamData[params[0]]["isBot"] = True
    #add defaults for other params too
    teams[teamData[params[0]]["team"]].append(teamData[params[0]])

async def auto_populate(teams):
    print(teams)
    for key, value in teamData.items():
        position = teamData[key]["position"]
        team = teamData[key]["team"]
        if teams==team:
            if position == "Beater":
                if team_rosters[team]["Beater1"] == None:
                    team_rosters[team]["Beater1"] = key
                elif team_rosters[team]["Beater2"] == None:
                    team_rosters[team]["Beater2"] = key 
            elif position == "Chaser":
                if team_rosters[team]["Chaser1"] == None:
                    team_rosters[team]["Chaser1"] = key
                elif team_rosters[team]["Chaser2"] == None:
                    team_rosters[team]["Chaser2"] = key
                elif team_rosters[team]["Chaser3"] == None:
                    team_rosters[team]["Chaser3"] = key
            else:
                if position == "Keeper" and team_rosters[team]["Keeper"] == None:
                    team_rosters[team]["Keeper"] = key
                if position == "Seeker" and team_rosters[team]["Seeker"] == None:
                    team_rosters[team]["Seeker"] = key
    #TO-DO: finish this
    captains = await find_team_captain(teams)
    if(len(captains) != 0): #more complicated than I was hoping it would be
        print(captains)
        captain = captains[0]
        position = teamData[captain]["position"]
        print(position)


async def fill_roster_message(channel, team):
    team_roster_invalid = True
    for key, value in team_rosters[team].items():
        if value == None:
            team_roster_invalid = True
            continue
    team_roster_invalid = False
    return team_roster_invalid

@client.event
async def on_message(message):
    global gameStarted
    if message.author.bot:
        return;
    if(gameStarted): #feed the input directly to an asynchronous method designed to handle input for when the game is actually started
        if(team_a and team_b):
            if(team_a != "Gryffindor" and team_b != "Gryffindor"):
                if(message.content.find("-stop") != 1):
                    await message.channel.send("Cannot send messages while a game is going on")
        if(message.content.find('continue') != -1):
            global control_sequence
            control_sequence = True
            return
    if(message.content.find("-set") != -1): #valid command makes 4 arguments
    #-set -p [position_name] [player_name]
        generator = (entry for entry in message.author.roles if entry.name=="Admin")
        role = next(generator, None)
        if(teamData[message.author.name]["captain"] == True or role != None):
            m = message.content.split()
            print(m)
            if(len(m) != 4 or m[1] != "-p"):
                await message.channel.send("Invalid command. Try using -help -set for more info")
                return
            await set(message.channel, m, role)
        else:
            await message.channel.send("Can't use the -set command unless you're a captain for an admin")
    elif message.content.find("-help") != -1: 
        await message.channel.send(help_string)
    elif message.content.find("-name") != -1:
        m = message.content.split()
        await search_for_param("name", m, message.channel)

    elif message.content.find("-position") != -1:
        m = message.content.split()
        await search_for_param("position", m, message.channel)

    elif message.content.find("-year") != -1:
        m = message.content.split()
        await search_for_param("year", m, message.channel)

    elif message.content.find("-rank") != -1:
        m = message.content.split()
        await search_for_param("rank", m, message.channel)

    elif message.content.find("-xp") != -1:
        m = message.content.split()
        await search_for_param("xp", m, message.channel)

    elif message.content.find("-score") != -1:
        if(not gameStarted):
            await message.channel.send("No game is ongoing")
            return
        await message.channel.send("Score is " + team_a + ": " + str(scores[team_a]) + ", " +  team_b + ": " + str(scores[team_b]))
        
    elif message.content.find("-captain") != -1:
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

    elif message.content.find("-write") != -1: #helper function for quickly writing extra parameters to the json file without extra hassle
        m = message.content.split()
        if(len(m) != 4):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        param = m[1]
        default_value = m[2]
        type = m[3]
        if(type == "boolean"):
            default_value = eval(default_value)
        elif(type == "int"):
            default_value = int(default_value)
        await write_params(param, default_value, message.channel)

    elif message.content.find("-roster") != -1:
        m = message.content.split()
        if(len(m) != 2):
            await message.channel.send("Couldn't recognize that command. Try -help")
            return
        team = m[1]
        if team not in team_rosters:
            await message.channel.send("Didn't recognize the team name")
            return
        return_message = team
        for key, value in team_rosters[team].items():
            return_message += "\n" + key + "\t" + str(value)
        print(return_message)
        await message.channel.send(return_message)

    elif message.content.find("-autopop") != -1: #autopopulate command takes one argument
        if(gameStarted):
            return
        m = message.content.split()
        if(len(m) != 2):
            await message.channel.send("Incorrect number of arguments")
            return
        team = m[1]
        await auto_populate(team)

    elif message.content.find("-start") != -1: #have start take one to two arguments
        #if there is one argument in the entry, assume that the game is between the team provided and Gryffindor
        m = message.content.split()
        if(gameStarted):
            return
        if(len(m) != 2 and len(m) != 3):
            message.channel.send("Invalid number of arguments")
        print("Start")
        if(len(m) == 2):
            team = m[1]
            if team not in teams:
                await message.channel.send("Not a valid team name")
                return
            print(team_rosters[team])
            for key, value in team_rosters[team].items():
                if value == None:
                    await message.channel.send("Invalid roster")
                    return
            for key, value in team_rosters["Gryffindor"].items():
                if value == None:
                    await message.channel.send("Invalid roster")
                    return
            await message.channel.send("Match is ready to start!")
            await start_match(message.channel, "Gryffindor", team)
        else:
            teamA = m[1]
            teamB = m[2]
            if teamA not in teams:
                await message.channel.send(teamA + " not a valid team name")
                return
            if teamB not in teams:
                await message.channel.send(teamB + " not a valid team name")
                return
            if teamA == "Gryffindor" or teamB == "Gryffindor":
                await message.channel.send("This doesn't make a whole lot of sense")
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
            await start_match_headless(message.channel, teamA, teamB)
    elif message.content.find("-add") != -1:
        args = message.content.split()
        required_args = [" name", " position", " team", " captain"]
        for arg in required_args:
            if(message.content.find(arg) == -1):
                await message.channel.send(arg + " is required")
                return
        await add_player(args[1:])
        await message.channel.send("Successfully added " + str(args[1]))

    elif message.content.find("-save") != -1:
        await save(message.channel)

    elif message.content.find("-sub") != -1: #similar in principle to sub but sub subs in a character who already is in the game
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
                print(teamData[key]["injured"])
                if(teamData[key]["critically_injured"] == True):
                    await message.channel.send(key + " (critically injured)")
                elif(teamData[key]["injured"] == True):
                    await message.channel.send(key + " (injured)")
                else:
                    await message.channel.send(key)
    elif message.content.find("-clear") != 1: #clears rank and xp
        await clear()
    elif message.content.find("-pause") != 1:
        if(gameStarted):
            gameStarted = False
            await message.channel.send("Game stopped")
        else:
            await message.channel.send("No game in progress")
    else:
        await message.channel.send("Couldn't recognize that command. Try -help")

client.run(os.getenv("TOKEN"))