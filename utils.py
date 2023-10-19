import random

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
            name = "Seeker_" + team + str(len(list))
            teams[team].append(replacement)
            new_player = True
        pos = "Seeker"
    if(new_player):
        string = "-add {r} name {n} position {p} team {t} captain false"
        print(string.format(r = replacement, n = name, p = pos, t = team))
        await add_player(string.format(r = replacement, n = name, p = pos, t = team))
    print("Player to sub in: " + replacement)
    team_rosters[team][position[0]] = replacement
    print(team_rosters[team])
    
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

class FlavorTextGenerator():
    def __init__(self, flavorText):
        self.flavorText = flavorText

    async def generateNextText(self, textType):
        index = random.randint(0, len(self.flavorText["hits"][textType])-1)
        return self.flavorText["hits"][textType][index]

    async def generateNextMissText(self, textType):
        index = random.randint(0, len(self.flavorText["misses"][textType])-1)
        return self.flavorText["misses"][textType][index]

    async def generateNextBeaterText(self, textType, position="beater"):
        if(textType == "fouls"):
            index = random.randint(0, len(self.flavorText["fouls"][position])-1)
            return self.flavorText[textType][position][index]
        index = random.randint(0, len(self.flavorText[textType])-1)
        return self.flavorText[textType][index]

    async def generateNextMove(self, moveType):
        index = random.randint(0, len(self.flavorText["moves"][moveType])-1)
        return self.flavorText["moves"][moveType][index]
    
    async def generateNextActionText(self):
        index = random.randint(0, len(self.flavorText["fouls"]["moves"]))
        return self.flavorText["fouls"]["moves"][index]