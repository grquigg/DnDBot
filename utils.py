import random

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

async def generateNextText(textType, flavorText):
    index = random.randint(0, len(flavorText["hits"][textType])-1)
    return flavorText["hits"][textType][index]

async def generateNextMissText(textType):
    index = random.randint(0, len(flavorText["misses"][textType])-1)
    return flavorText["misses"][textType][index]

async def generateNextBeaterText(textType, position="beater"):
    if(textType == "fouls"):
        index = random.randint(0, len(flavorText["fouls"][position])-1)
        return flavorText[textType][position][index]
    index = random.randint(0, len(flavorText[textType])-1)
    return flavorText[textType][index]


async def generateNextMove(moveType):
    index = random.randint(0, len(flavorText["moves"][moveType])-1)
    return flavorText["moves"][moveType][index]